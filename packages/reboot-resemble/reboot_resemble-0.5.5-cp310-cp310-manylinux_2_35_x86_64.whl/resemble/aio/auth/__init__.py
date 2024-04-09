from dataclasses import dataclass
from resemble.aio.auth.tokens import Token
from typing import Optional


@dataclass(kw_only=True)
class Auth:
    """Dataclass for storing auth specific details specific to an implementation
    (e.g., depending which identity provider you use, how you do authorization,
    etc). We include some fields that we believe are generic to simplify
    implementations such as user id and bearer token.

    The Auth object is provided by the TokenVerifier and passed on the context
    on every request.
    """
    user_id: Optional[str] = None
    bearer_token: Optional[Token] = None
