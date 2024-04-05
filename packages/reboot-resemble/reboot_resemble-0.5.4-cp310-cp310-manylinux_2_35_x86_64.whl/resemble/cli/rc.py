import argparse
import git
# mypy fails with 'error: Trying to read deleted variable "exc"' if we use
# 'git.exc'
import git.exc as gitexc
import os
import re
import shlex
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from resemble.cli import terminal
from resemble.cli.terminal import fail
from typing import Any, Optional

# Type aliases to help better understand types.
Subcommand = str
Config = str
Flag = str
Flags = defaultdict[tuple[Subcommand, Optional[Config]], list[Flag]]

# String representing flags for "common" expansion.
COMMON_PATTERN = '...'

# Regular expressions for matching lines in the .rc file.
#
# A line in the .rc file consists of a subcommand, an optional config, and a
# list of arguments.
#
# A subcommand is either a sequence of words separated by spaces, e.g., 'foo bar
# baz' or the COMMON_PATTERN above.
# Each word in a sequence must start with a letter and can contain letters,
# numbers, and hyphens. A word can not start with a hyphen or a number.
SUBCOMMAND_REGEX = '(%s|%s)' % (
    re.escape(COMMON_PATTERN),
    r'([a-zA-Z][a-zA-Z0-9-]*(?:\s+[a-zA-Z][a-zA-Z0-9-]*)*)',
)
# A config starts with a letter but can contain letters, numbers, and hyphens.
CONFIG_REGEX = r'[a-zA-Z][a-zA-Z0-9-]*'
# An argument is a sequence of non-space characters.
ARGUMENTS_REGEX = r'(([^\s]+)\s*)+'


class StoreOnceAction(argparse.Action):
    """Helper action that ensures that only one instance of a flag that is
    not meant to be repeated is present.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Record which `id(namespace)`s we've seen `self.dest` in. We can't just check
        # whether or not we the flag is `None` in `namespace` (e.g., via
        # `getattr(namespace, ...)` because it might not be `None` if there is a default
        # value.
        self._already_seen_for_namespace: set[int] = set()

    def __call__(self, parser, namespace, values, option_string=None):
        namespace_id = id(namespace)
        if namespace_id in self._already_seen_for_namespace:
            parser.error(
                f"found more than one instance of --{self.dest.replace('_', '-')}=VALUE"
            )
        else:
            self._already_seen_for_namespace.add(namespace_id)
            setattr(namespace, self.dest, values)


class TransformerError(ValueError):
    """Raised when a transformer fails to transform a value."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BaseTransformer(ABC):
    """Base class a transformer.

    When an argument is being parsed, a transformer can modify the
    user-provided flag values to take a different shape than the original input.
    For example, a transformer could make all letters in a flag value uppercase,
    or split a comma separated string, e.g., `'string,of,words'.split(',')`.
    """

    @abstractmethod
    def transform(self, value: str) -> Any:
        raise NotImplementedError


class SubcommandParser:
    """Helper class that encapsulates an `argparse.ArgumentParser` so that
    we can control how arguments are added and to validate them for
    correctness and consistency with other args.
    """

    _parser: argparse.ArgumentParser
    _subparsers: Optional[argparse._SubParsersAction]

    _argument_types: dict[str, type]

    def __init__(self, subcommand: str, parser: argparse.ArgumentParser):
        self._subcommand = subcommand
        self._parser = parser
        self._subparsers = None
        self._argument_types: dict[str, type] = {}
        self._transformers: dict[str, Optional[BaseTransformer]] = {}

    def add_argument(
        self,
        name: str,
        *,
        type: type,
        help: str,
        repeatable: bool = False,
        required: Optional[bool] = None,
        default: Optional[Any] = None,
        transformer: Optional[BaseTransformer] = None,
    ) -> None:
        """Adds an argument. Unlike `argparse.ArgumentParser` this requires
        `type` and `help` so that we ensure we create a better
        experience for our end users.
        """
        if not self.is_leaf():
            raise ValueError(
                'Cannot add arguments to a subcommand that has subcommands '
                'itself'
            )

        if name.startswith('-') and not name.startswith('--'):
            raise ValueError(
                f"Invalid argument '{name}': flags must start "
                "with '--' not '-'"
            )

        elif name.startswith('--') and '_' in name:
            raise ValueError(
                f"Invalid argument '{name}': flags must use kebab case"
            )

        elif repeatable and default is not None:
            raise ValueError(
                f"Invalid argument '{name}': can not be "
                "'repeatable' and have a 'default'"
            )

        elif repeatable and type == bool:
            raise ValueError(
                f"Invalid argument '{name}': 'bool' "
                "arguments can not be 'repeatable'"
            )

        kwargs: dict[str, Any] = {
            'type': type,
            'help': help,
        }

        if type is bool:
            kwargs['action'] = argparse.BooleanOptionalAction
        elif repeatable:
            if name.startswith('--'):
                # Repeated flags use the 'append' action.
                kwargs['action'] = 'append'
            else:
                # Repeated positional arguments use 'nargs'.
                if required:
                    kwargs['nargs'] = '+'
                else:
                    kwargs['nargs'] = '*'
        elif name.startswith('--'):
            kwargs['action'] = StoreOnceAction

        if name.startswith('--') and required is not None:
            kwargs['required'] = required

        if default is not None:
            kwargs['default'] = default

        self._parser.add_argument(name, **kwargs)

        self._argument_types[name] = type
        self._transformers[name] = transformer

    def is_leaf(self) -> bool:
        """Returns `True` if this subcommand has no subcommands."""
        return self._subparsers is None

    def get_argument_type(self, name: str) -> Optional[type]:
        """Helper that returns the type of an argument value."""
        return self._argument_types.get(name, None)

    def get_transformer(self, name: str) -> Optional[BaseTransformer]:
        """Returns the specified argument's transformer or `None`."""
        return self._transformers.get(name, None)

    def get_subparsers(self) -> argparse._SubParsersAction:
        """Create subcommand parser for the subcommand."""
        if self._subparsers is None:
            self._subparsers = self._parser.add_subparsers(
                dest=self._subcommand, required=True
            )

        return self._subparsers


class HelpFormatter(argparse.HelpFormatter):
    """Helper formatter that replaces all '--flag FLAG' with
    '--flag=FLAG'.
    """

    def format_help(self) -> str:
        # Get the default formatted help.
        help = super().format_help()

        # And replace all '--flag FLAG' with '--flag=FLAG'.
        return re.sub(r'(--[a-z-]+)[ ]([A-Z_]+)', r'\1=\2', help)


class ArgumentParser:
    """A CLI argument/options/flags parser that knows how to expand
    arguments found in a '.rc', e.g, '.rsmrc'.

    Formatting expected in a '.rc' file:

    (1) Comments. Any line starting with a '#' is skipped. All text
        after a trailing '#' is also dropped.

    (2) "Common" flags, i.e., flags that are relevant for all
        subcommands, defined by the top-level parser, are
        distinguished via a line that starts with {COMMON_PATTERN},
        e.g., '...':

        # Always expanded.
        ... --more-flags=42 and_args here

    (3) Subcommand specific flags:

        # Always expanded when invoking subcommand.
        subcommand --more-flags=42 and_args here

    (4) Config flags expanded from '--config=foo' for both "common"
        and subcommands:

        # Only expanded if --config=foo.
        ...:foo --flag=42
        subcommand:foo --more-flags=42

    (5) Recursive configs are fully supported:

        dev:fullstack --fullstack

        dev:demo --config=fullstack

    (6) All lines are aggregated.

        dev:demo --config=fullstack  # The demo is "fullstack".
        dev:demo --name=demo         # Name of demo.
        dev:demo --python            # Uses Python.


    TODO(benh): move this into own file 'rc_argument_parser.py'
    if/once we need it for other CLI tools.
    """

    def __init__(
        self,
        *,
        program: str,
        filename: str,
        subcommands: list[str],
        rc_file: Optional[str] = None,
        argv: Optional[list[str]] = None,
        cwd: Optional[str] = None
    ):
        self._parser = argparse.ArgumentParser(
            prog=program,
            allow_abbrev=False,
            # We need our own formatter class so we output
            # '--flag=FLAG' not '--flag FLAG'.
            formatter_class=HelpFormatter,
        )
        self._rc_filename = filename
        self._cwd = Path(os.getcwd())

        rsm_version: str
        try:
            rsm_version = version('reboot-resemble')
        except PackageNotFoundError:
            # If rsm is running in not-a-built-wheel-package.
            rsm_version = '<unreleased build>'

        self._parser.add_argument(
            '--version',
            action='version',
            version=rsm_version,
        )

        top_level_subparsers = self._parser.add_subparsers(
            dest='subcommand', required=True
        )

        self._subcommand_parsers: dict[str, SubcommandParser] = {}

        def get_or_create_subcommand_parser(
            subcommand: str
        ) -> SubcommandParser:
            """Helper function for recursively populating
            `self._subcommand_parsers`.

            Each nested subcommand parser is linked to it's parent parser. The
            top level parser is the one of the `ArgumentParser` instance.
            """

            # If the subcommand parser already exists, return it.
            if subcommand in self._subcommand_parsers:
                return self._subcommand_parsers[subcommand]

            # Split the subcommand into segments, e.g., 'foo bar baz' -> ['foo',
            # 'bar', 'baz'].
            segments = subcommand.split(' ')

            # There can be no empty string segments caused by multiple spaces.
            assert all([len(segment.strip()) > 0 for segment in segments])

            # The parent subcommand is all segments except the last one. E.g.,
            # for 'foo bar baz' the parent subcommand is 'foo bar' while the
            # current subcommand is 'baz'.
            parent_subcommand = ' '.join(segments[:-1])
            current_subcommand = segments[-1]

            # In order to create a subcommand, we need to get the parent
            # subcommand parser so we can update its `argparse` subparsers.
            parent_subparsers: argparse._SubParsersAction

            if parent_subcommand == '':
                # If there is no parent subcommand, we are at the top level.
                parent_subparsers = top_level_subparsers
            else:
                # Get or create the parent subcommand parser.
                parent_subparsers = get_or_create_subcommand_parser(
                    parent_subcommand
                ).get_subparsers()

            # We create the current subcommand parser as a new parser of the
            # parent subparser.
            subparser = parent_subparsers.add_parser(
                current_subcommand,
                allow_abbrev=False,
                # We need our own formatter class so we output
                # '--flag=FLAG' not '--flag FLAG'.
                formatter_class=HelpFormatter,
            )

            # Create our helper class for the subcommand parser, store it, and
            # return it.
            self._subcommand_parsers[subcommand] = SubcommandParser(
                subcommand, subparser
            )
            return self._subcommand_parsers[subcommand]

        for subcommand in subcommands:

            if not re.match(SUBCOMMAND_REGEX, subcommand):
                raise ValueError(f"Invalid subcommand '{subcommand}'")

            # Recursively populate `self._subcommand_parsers` by creating
            # necessary parent subparsers as we go.
            subparser = get_or_create_subcommand_parser(subcommand)

            # Add the `--config` parameter to all subcommands.
            subparser.add_argument(
                '--config',
                repeatable=True,
                type=str,
                help=f"\"configs\" to apply from a '{filename}' file, "
                f"e.g., 'rsm {subcommand} --config=foo' would add all flags "
                f"on lines in the '{filename}' that start with '{subcommand}:foo'",
            )

        argv = argv or list(sys.argv)

        self._help = '-h' in argv or '--help' in argv

        # Don't bother trying to expand args/flags from a '.rc' if the
        # user is asking for help because expanding args/flags means
        # calling `self._parser.parse_known_args(...)` and `argparse`
        # will see that '--help' or '-h' and print out a help message
        # that doesn't include all of the actual args/flags that will
        # get added after this constructor returns.
        if self._help:
            self._argv = argv
            self._subcommand = None
            return

        # Try to expand flags from a '.rc'
        if rc_file is not None:
            rc_file = os.path.abspath(rc_file)
            if not os.path.isfile(rc_file):
                fail(f"Failed to find {filename} at {rc_file}")
            if not os.access(rc_file, os.R_OK):
                fail(f"Found '{filename}' at {rc_file} but it is not readable")

        self.dot_rc: Optional[str] = (
            rc_file or ArgumentParser._find_dot_rc(filename)
        )

        # Parse command line but only looking for subcommands and
        # '--config=' flags.
        self._initial_namespace, _ = self._parser.parse_known_args(
            args=argv[1:]
        )
        self._subcommand = self._update_subcommand_in_namespace(
            self._initial_namespace
        )

        self._argv = argv

    @staticmethod
    def strip_any_arg(
        argv: list[str],
        *queried_args: str,
    ) -> tuple[bool, list[str]]:
        """A very basic static check for the presence of any of a set of argument names."""
        # Note: This is located in this module because it might eventually want
        # to grow into a full parse of a set of "bootstrap" arguments.
        result_argv = [arg for arg in argv if arg not in queried_args]
        return len(argv) != len(result_argv), result_argv

    def subcommand(self, subcommand: str) -> SubcommandParser:
        """Returns the parser for the specified subcommand."""
        if subcommand not in self._subcommand_parsers:
            raise ValueError(f"Invalid subcommand '{subcommand}'")
        return self._subcommand_parsers[subcommand]

    def parse_args(self) -> tuple[argparse.Namespace, list[str]]:
        """Pass through to top-level parser with the expanded arguments after
        first validating that all flags include '=' between them and their value."""

        if self._help:
            return self._parser.parse_args(args=self._argv[1:]), []

        # We must have the subcommand at this point so that we can
        # call `self._get_argument_type(...)`.
        assert self._subcommand is not None

        # Normalize the args that arrived from `sys.argv` relative to the current directory,
        # and then expand arguments from the rc file.
        args = self._normalize_path_arguments(self._cwd, self._argv)
        args = self._expand_dot_rc(args)

        # Try to get the 'args_after_dash_dash' after we expand flags from
        # .rsmrc so that we can properly handle '--' in the .rsmrc file.
        try:
            dash_dash_index = args.index('--')
            args_after_dash_dash = args[dash_dash_index + 1:]
            args = args[:dash_dash_index]
        except ValueError:
            args_after_dash_dash = []

        # Ensure all non-boolean flags include '=', e.g.,
        # '--flag=value'.
        for i in range(len(args)):
            arg = args[i]
            if arg.startswith('--'):
                parts = arg.split('=', 1)
                assert len(parts) > 0
                arg_type: Optional[type] = self._get_argument_type(parts[0])

                if arg_type is None:
                    # Let `argparse` handle any invalid arguments.
                    continue

                if len(parts) == 1 and arg_type != bool:
                    # Try and guess what the user intended by printing
                    # out "did you mean {arg}={args[i + 1]" assuming
                    # that there is an `i + 1` argument.
                    did_you_mean = ""
                    if i + 1 < len(args):
                        quote = "'" if " " in args[i + 1] else ""
                        did_you_mean = f" (did you mean {arg}={quote}{args[i + 1]}{quote})"

                    self._parser.error(
                        f"expected {arg}=VALUE, missing '=VALUE'{did_you_mean}"
                    )

        namespace: argparse.Namespace = self._parser.parse_args(args=args)
        assert self._subcommand == self._update_subcommand_in_namespace(
            namespace
        )

        # Now let's apply any transformers to the parsed arguments.
        subcommand_parser = self._subcommand_parsers[self._subcommand]
        for name in vars(namespace):
            # After parsing, we have names without the '--' prefix. Since
            # we allow flags only with '--' prefix, we can add it back here,
            # to get the transformer.
            transformer = subcommand_parser.get_transformer('--' + name)
            if transformer is not None:
                value = getattr(namespace, name)
                if value is not None:
                    try:
                        if isinstance(value, list):
                            value = [transformer.transform(v) for v in value]
                        else:
                            value = transformer.transform(value)
                    except TransformerError as e:
                        self._parser.error(e.message)
                    else:
                        setattr(namespace, name, value)

        return namespace, args_after_dash_dash

    def _get_argument_type(self, arg: str) -> Optional[type]:
        """Helper for getting an argument type from the correct parser given
        the subcommand that was determined during initialization."""
        # Subcommands are required when parsing, so we could not have
        # gotten here if we do not have a valid subcommand.
        assert self._subcommand is not None
        assert self._subcommand in self._subcommand_parsers

        return self._subcommand_parsers[self._subcommand
                                       ].get_argument_type(arg)

    def _normalize_path_arguments(self, root: Path,
                                  args: list[str]) -> list[str]:
        """If any of the given arguments are of type `Path` and are relative, make them absolute."""

        def _normalize(arg: str) -> str:
            split_arg = arg.split("=", 1)
            if len(split_arg) != 2:
                return arg
            arg_name, arg_value = split_arg
            if not self._get_argument_type(arg_name) == Path:
                return arg
            path = Path(arg_value)
            if path.is_absolute():
                return arg
            return f"{arg_name}={str(root / path)}"

        return [_normalize(arg) for arg in args]

    @staticmethod
    def _find_dot_rc(filename: str) -> Optional[str]:
        """Tries to find the '.rc' file in the current directory or, if in a
        git repository, in the top-level directory of the repository,
        and returns the path if found otherwise `None`."""
        dot_rc: Optional[str] = None

        dot_rc = os.path.join(os.getcwd(), filename)
        if not os.path.isfile(dot_rc):
            try:
                repo = git.Repo(search_parent_directories=True)
            except gitexc.InvalidGitRepositoryError:
                return None
            else:
                dot_rc = os.path.join(repo.working_dir, filename)
                if not os.path.isfile(dot_rc):
                    return None

        assert dot_rc is not None

        if not os.access(dot_rc, os.R_OK):
            fail(f"Found '{filename}' at {dot_rc} but it is not readable")

        return os.path.abspath(dot_rc)

    @staticmethod
    def _update_subcommand_in_namespace(
        namespace: argparse.Namespace,
    ) -> Subcommand:
        """Removes subcommand nesting in the given namespace, and returns the complete subcommand."""

        # Subcommands are required.
        assert namespace.subcommand is not None

        # We need to build the full command from entries in the namespace.
        # The namespace can be thought of glorified dictionary of key value
        # pairs. Each key is a subcommand - including spaces - pointing to
        # the next subcommand. The key of the initial subcommand is
        # 'subcommand'.
        # For 'foo bar baz boo', the namespace would look like:
        #   namespace = {
        #       'subcommand': 'foo',
        #       'foo': 'bar',
        #       'foo bar': 'baz',
        #       'foo bar baz': 'boo',
        #   }
        # Since a namespace does not support bracket indexing, e.g., `namespace['foo
        # bar']`, we use `getattr` below to access the keys. We'd have to do the
        # same to access values that contains spaces or dots as neither
        # `namespace.foo bar` nor `namespace.foo bar.baz` are valid python. The
        # alternative is to cast the namespace to a dictionary and use bracket
        # indexing.
        #
        # When we have accessed the last key, we have the full subcommand and we
        # know that we've reached the end when `getattr` raises an
        # `AttributeError`. For the example above, when we would try and get the
        # value of 'foo bar baz boo'.
        def build_subcommand(subcommand: str):
            if not hasattr(namespace, subcommand):
                return subcommand

            result = build_subcommand(
                subcommand + ' ' + getattr(namespace, subcommand)
            )
            delattr(namespace, subcommand)
            return result

        result = build_subcommand(namespace.subcommand)
        namespace.subcommand = result
        return result

    def _read_flags_from_dot_rc(
        self,
        filename: str,
        dot_rc: str,
    ) -> Flags:
        """Returns the flags that should be added to the command line, keyed by
        the subcommand and config for those flags, or the empty tuple if
        they should be applied to all command lines.
        """

        # Instead of using the SUBCOMMAND_REGEX directly, we exploit that we
        # know all possible values of (nested) subcommands and can construct a
        # pattern that matches only the registered valid subcommands.
        valid_subcommands = [
            subcommand
            for subcommand, parser in self._subcommand_parsers.items()
            if parser.is_leaf()
        ]
        VALID_SUBCOMMAND_REGEX = '|'.join(
            [re.escape(COMMON_PATTERN)] +
            [re.escape(subcommand) for subcommand in valid_subcommands]
        )

        # A line in the .rc file consists of a subcommand, an optional config, and
        # multiple arguments.
        rc_line_regex = re.compile(
            f'(?P<subcommand>{VALID_SUBCOMMAND_REGEX})(:(?P<config>{CONFIG_REGEX}))?\s(?P<arguments>{ARGUMENTS_REGEX})'
        )

        flags: Flags = defaultdict(list)

        dot_rc_dir = Path(dot_rc).parent
        with open(dot_rc, 'r') as file:
            line_number = 0
            for line in file.readlines():
                line_number += 1
                line = line.strip()  # Remove leading and trailing whitespaces.

                # Remove any trailing comments.
                line = line.split('#', 1)[0]

                # Skip empty lines. This includes lines that previously had only
                # comments as we've stripped these above.
                if len(line) == 0:
                    continue

                # Match line against valid syntax.
                match = rc_line_regex.match(line)
                if match is None:
                    # The line is not a valid line, but we can still provide a
                    # more helpful error message.

                    # Check if the line contains a valid subcommand. If it does
                    # not, print an error message that includes the available
                    # subcommands.
                    if not re.search(fr'^\s*({VALID_SUBCOMMAND_REGEX})', line):
                        invalid_subcommand = re.split('[-\:]', line)[0].strip()
                        fail(
                            f"'{invalid_subcommand}' found at {dot_rc}:{line_number} "
                            "is not a valid subcommand (available subcommands: "
                            f"{', '.join(valid_subcommands)})"
                        )
                    else:
                        # Catch all. We failed to parse the line.
                        fail(
                            f"Failed to parse '{filename}' file at {dot_rc}:{line_number}:\n'{line}'"
                        )

                # For mypy that does not understand `fail`.
                assert match is not None

                # Extract matches and split arguments.
                subcommand: str = match.group('subcommand')
                config: Optional[str] = match.group('config')
                arguments: list[str] = self._normalize_path_arguments(
                    dot_rc_dir, shlex.split(match.group('arguments'))
                )

                # Update flags.
                flags[(subcommand, config)].extend(arguments)

        return flags

    def _expand_dot_rc(
        self,
        argv: list[str],
    ) -> list[str]:
        """Expand '.rc' file into `argv`."""
        if self.dot_rc is None:
            return argv[1:]
        assert self._subcommand is not None

        filename = self._rc_filename
        subcommand = self._subcommand
        argv = list(argv)

        flags = self._read_flags_from_dot_rc(self._rc_filename, self.dot_rc)

        # Now add all "common" flags.
        common_flags = flags[(COMMON_PATTERN, None)]
        if len(common_flags) > 0:
            argv = argv[:1] + common_flags + argv[1:]

        subcommand_flags: list[Flag] = []

        # Now add '{subcommand}' specific flags.
        subcommand_flags = flags[(subcommand, None)]
        if len(subcommand_flags) > 0:
            argv.extend(subcommand_flags)

        # Parse the known args again since we might have added some
        # configs from '{subcommand}'.
        namespace, _ = self._parser.parse_known_args(args=argv[1:])

        assert subcommand == self._update_subcommand_in_namespace(namespace)

        # Now expand config flags.
        configs = namespace.config or []

        common_config_flags: dict[Config, list[Flag]] = {}
        subcommand_config_flags: dict[Config, list[Flag]] = {}

        while not all(
            (config in common_config_flags) and
            (config in subcommand_config_flags) for config in configs
        ):
            for config in configs:
                # In order for 'config' to be valid we must find
                # either '{COMMON_PATTERN}:{config}' or
                # '{subcommand}:{config}' in the '{self.dot_rc}' file.
                expanded = (
                    config in common_config_flags and
                    config in subcommand_config_flags
                )

                # Expand '{COMMON_PATTERN}:{config}' flags, but prepend
                # those (after `argv[0]`, but before `argv[1]`).
                if config not in common_config_flags:
                    if (COMMON_PATTERN, config) in flags:
                        expanded = True
                        common_config_flags[config] = flags[
                            (COMMON_PATTERN, config)]
                        argv = argv[:1] + common_config_flags[config] + argv[1:]
                    else:
                        # Store the config so we know it was processed and
                        # we can halt the otherwise infinite while loop.
                        common_config_flags[config] = []

                # Expand '{subcommand}:{config}' flags.
                if config not in subcommand_config_flags:
                    if (subcommand, config) in flags:
                        expanded = True
                        subcommand_config_flags[config] = flags[
                            (subcommand, config)]
                        argv.extend(subcommand_config_flags[config])
                    else:
                        # Store the config so we know it was processed and
                        # we can halt the otherwise infinite while loop.
                        subcommand_config_flags[config] = []

                if not expanded:
                    fail(
                        f"--config={config} is invalid, no "
                        f"'{COMMON_PATTERN}:{config}' nor '{subcommand}:{config}' "
                        f"lines found in {self.dot_rc}"
                    )

            # Now re-parse the known args so we can see whether or not
            # expanding the last configs added any more configs that
            # we need to continue expanding.
            #
            # NOTE: we pass a copy of `argv` here so that we don't
            # mutate the original `argv` which we'll need to use for
            # our ultimate parsing, after we've expanded all of the
            # configs.
            namespace, _ = self._parser.parse_known_args(args=argv[1:])

            assert subcommand == self._update_subcommand_in_namespace(
                namespace
            )
            configs = namespace.config

        if terminal.is_verbose() and (
            len(common_flags) > 0 or len(subcommand_flags) > 0 or
            len(subcommand_config_flags) > 0
        ):
            terminal.verbose(
                f"Expanded flags from '{filename}' located at {self.dot_rc}"
            )
            if len(common_flags) > 0:
                terminal.verbose(
                    f"    {' '.join(common_flags)} (from '{COMMON_PATTERN}' in '{filename}')"
                )

            if len(subcommand_flags) > 0:
                terminal.verbose(
                    f"    {' '.join(subcommand_flags)} (from '{subcommand}' in '{filename}')"
                )

            for config, config_flags in common_config_flags.items():
                if len(config_flags) > 0:
                    terminal.verbose(
                        f"    {' '.join(config_flags)} (from '{COMMON_PATTERN}:{config}' in '{filename}' via --config={config})"
                    )

            for config, config_flags in subcommand_config_flags.items():
                if len(config_flags) > 0:
                    terminal.verbose(
                        f"    {' '.join(config_flags)} (from '{subcommand}:{config}' in '{filename}' via --config={config})"
                    )

            # Print a newline here for some extra spacing between any other output or errors.
            terminal.verbose("")
        return argv[1:]
