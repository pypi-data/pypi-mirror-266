from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    AuthenticationFailed,
)
from rest_framework_simplejwt.settings import api_settings as jwt_settings
import requests
from .settings import api_settings
from .utils import enforce_csrf
from .views import unset_jwt_cookies


def set_jwt_access_cookie(response, access_token):
    cookie_name = api_settings.JWT_AUTH_COOKIE
    access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
    cookie_secure = api_settings.JWT_AUTH_SECURE
    cookie_httponly = api_settings.JWT_AUTH_HTTPONLY
    cookie_samesite = api_settings.JWT_AUTH_SAMESITE
    cookie_domain = api_settings.JWT_AUTH_COOKIE_DOMAIN

    if cookie_name:
        response.set_cookie(
            cookie_name,
            access_token,
            expires=access_token_expiration,
            secure=cookie_secure,
            httponly=cookie_httponly,
            samesite=cookie_samesite,
            domain=cookie_domain,
        )


class JWTStatelessCookieAuthMiddleware:  # pylint: disable=too-few-public-methods
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_changed = False
        access = request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)

        if access is None:  # TODO удалить т.к. это временная система
            refresh = request.COOKIES.get(api_settings.JWT_AUTH_REFRESH_COOKIE)
            if refresh is None:
                return self.get_response(request)

            refresh_response = requests.post(
                api_settings.JWT_REFRESH_URL, data={"refresh": refresh}, timeout=10
            )

            if refresh_response.status_code != status.HTTP_200_OK:
                response = self.get_response(request)
                unset_jwt_cookies(response)
                return response

            access = refresh_response.json().get("access")
            request.META[jwt_settings.AUTH_HEADER_NAME] = (
                f"{jwt_settings.AUTH_HEADER_TYPES[0]} {access}"
            )
            access_changed = True

        if api_settings.JWT_AUTH_COOKIE_USE_CSRF:
            enforce_csrf(request)

        authentication = JWTStatelessUserAuthentication()

        try:
            validated_token = authentication.get_validated_token(access)
            request.user = authentication.get_user(validated_token)
        except (InvalidToken, AuthenticationFailed):
            return self.get_response(request)

        response = self.get_response(request)

        if access_changed:
            set_jwt_access_cookie(response, access)

        return response
