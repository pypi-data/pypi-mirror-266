import base64
from datetime import datetime, timezone
from typing import Callable
from functools import wraps

import cbor2

from antimatter.errors import errors
from antimatter.session_mixins.verification_mixin import ADMIN_VERIFICATION_PROMPT


def exec_with_token(f: Callable):
    """
    Decorator to get a token before executing the decorated function.

    :param f: The function to be decorated.
    :return: The wrapper function.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        def decode_token(t):
            decoded_bytes = base64.b64decode(t)
            if decoded_bytes[:7] == b"apikey:":
                # It is an API key, not a token, and we should invoke the refresh call.
                return None, None
            try:
                decoded_token = cbor2.loads(decoded_bytes)
                not_before = datetime.fromtimestamp(decoded_token.get("NotValidBefore"), timezone.utc)
                not_after = datetime.fromtimestamp(decoded_token.get("NotValidAfter"), timezone.utc)
            except:
                return None, None
            return not_before, not_after

        def is_token_valid(not_before, not_after):
            now_time = datetime.now(timezone.utc)
            return not_before and not_after and (not_before <= now_time <= not_after)

        token = self._client_func().api_client.configuration.access_token
        if not token:
            if not self._try_init_client():
                raise errors.SessionVerificationPendingError(ADMIN_VERIFICATION_PROMPT)
            token = self._client_func().api_client.configuration.access_token

        not_before, not_after = decode_token(token)

        if not is_token_valid(not_before, not_after):
            token = self.refresh_token()
            not_before, not_after = decode_token(token)

            if not is_token_valid(not_before, not_after):
                if not (not_before and not_after):
                    raise errors.TokenMalformed("malformed token detected")
                raise errors.TokenExpiredError("token has expired")

        # If all is good, we store the token.
        self._client_func().api_client.configuration.access_token = token

        # Call the decorated function.
        return f(self, *args, **kwargs)

    return wrapper
