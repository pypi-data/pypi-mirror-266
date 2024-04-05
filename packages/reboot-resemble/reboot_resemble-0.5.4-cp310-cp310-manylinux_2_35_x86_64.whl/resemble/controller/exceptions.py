from typing import Optional


class InputError(Exception):
    """Custom exception class used internally in the controller for handling
    errors related to user input."""

    def __init__(
        self,
        *,
        reason: str,
        parent_exception: Optional[Exception] = None,
    ):
        super().__init__(reason, parent_exception)
        self.reason = reason
        self.parent_exception = parent_exception
