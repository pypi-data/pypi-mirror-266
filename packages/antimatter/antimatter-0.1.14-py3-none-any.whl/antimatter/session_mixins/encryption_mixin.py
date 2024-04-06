from typing import Callable

from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class EncryptionMixin:
    """
    Session mixin defining CRUD functionality for encryption functionality.

    :param domain: The domain to use for the session.
    :param client: The client to use for the session.
    """

    def __init__(self, domain: str, client_func: Callable[[], DefaultApi], **kwargs):
        try:
            super().__init__(domain=domain, client_func=client_func, **kwargs)
        except TypeError:
            super().__init__()  # If this is last mixin, super() will be object()
        self._domain = domain
        self._client_func = client_func

    @exec_with_token
    def flush_encryption_keys(self):
        """
        Flush all keys in memory. The keys will be immediately reloaded from persistent
        storage, forcing a check that the domain's root key is still available
        """
        self._client_func().domain_flush_encryption_keys(domain_id=self._domain)
