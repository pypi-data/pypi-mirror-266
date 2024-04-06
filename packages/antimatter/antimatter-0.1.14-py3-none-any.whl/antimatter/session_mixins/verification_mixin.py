from typing import Callable, Optional

import antimatter.client as openapi_client
from antimatter.client import DefaultApi
from antimatter.errors import errors

ADMIN_VERIFICATION_PROMPT = (
    "domain not authenticated - check email to verify account; verification email "
    "can be sent again with session.resend_verification_email()"
)


class VerificationMixin:
    """
    Session mixin defining CRUD functionality for verification actions.
    """

    def __init__(self, domain: str, client_func: Callable[[], DefaultApi], email: Optional[str], **kwargs):
        try:
            super().__init__(domain=domain, client_func=client_func, email=email, **kwargs)
        except TypeError:
            super().__init__()  # If this is last mixin, super() will be object()
        self._domain = domain
        self._client_func = client_func
        self._email = email

    def resend_verification_email(self, email: Optional[str] = None):
        """
        Resend the verification email to the admin contact email. If the session
        was called with an email, that will be used if none is provided.

        :param email: The email to resend the verification email for.
        """
        if not email and not self._email:
            raise errors.SessionVerificationPendingError("unable to resend verification email: email unknown")

        self._client_func().domain_contact_issue_verify(
            domain_id=self._domain,
            domain_contact_issue_verify_request=openapi_client.DomainContactIssueVerifyRequest(
                admin_email=email or self._email,
            )
        )
