import logging

from pyramid.authorization import Authenticated, Everyone, ACLHelper
from pyramid.authentication import SessionAuthenticationHelper
from .identity import get_identity

logger = logging.getLogger(__name__)


class SessionSecurityPolicy:
    def __init__(self):
        self.helper = SessionAuthenticationHelper()

    def identity(self, request):
        """Return app-specific user object."""
        userid = self.helper.authenticated_userid(request)
        if userid is None:
            return None

        if getattr(request, "_cached_identity", None) is None:
            request._cached_identity = get_identity(request, userid)
        return request._cached_identity

    def authenticated_userid(self, request):
        """Return a string ID for the user."""

        identity = self.identity(request)

        if identity is None:
            return None

        return str(identity.id)

    def permits(self, request, context, permission):
        """Allow access to everything if signed in."""
        identity = self.identity(request)
        principals = [Everyone]
        if identity is not None:
            principals.append(Authenticated)
            principals.append(identity.login.login)
            principals.append(f"user:{identity.id}")
            principals.append(f"login:{identity.login.id}")
            for group in identity.login.groups:
                principals.append("group:{0}".format(group))
            for company in identity.companies:
                if company.active:
                    principals.append("company:{}".format(company.id))
        return ACLHelper().permits(context, principals, permission)

    def remember(self, request, userid, **kw):
        return self.helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        # Clean le cache
        if hasattr(request, "_cached_identity"):
            del request._cached_identity
        return self.helper.forget(request, **kw)
