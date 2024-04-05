from dataclasses import dataclass
from typing import Any, Optional


@dataclass(kw_only=True, frozen=True)
class Token:
    """Dataclass for working with authorization tokens.

    In case of an encoded token, such as a JWT, the decoded field can be used to
    store the token content.
    """
    raw: str
    decoded: Optional[dict[str, Any]] = None
