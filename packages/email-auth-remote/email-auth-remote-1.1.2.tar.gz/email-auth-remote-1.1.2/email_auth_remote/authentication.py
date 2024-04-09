"""Модуль аутентификации с помощью auth endpoint."""

import logging
from rest_framework_simplejwt.authentication import (
    JWTStatelessUserAuthentication,
)
from .settings import api_settings
from .utils import enforce_csrf

logger = logging.getLogger(__name__)


class JWTStatelessCookieAuthentication(JWTStatelessUserAuthentication):
    """
    An authentication plugin that hopefully authenticates requests through a JSON web
    token provided in a request cookie (and through the header as normal, with a
    preference to the header).
    """

    def authenticate(self, request):
        cookie_name = api_settings.JWT_AUTH_COOKIE
        header = self.get_header(request)
        if header is None:
            if cookie_name:
                raw_token = request.COOKIES.get(cookie_name)
                if (
                    api_settings.JWT_AUTH_COOKIE_ENFORCE_CSRF_ON_UNAUTHENTICATED
                ):  # True at your own risk
                    enforce_csrf(request)
                elif raw_token is not None and api_settings.JWT_AUTH_COOKIE_USE_CSRF:
                    enforce_csrf(request)
            else:
                return None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
