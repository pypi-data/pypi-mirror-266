from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck

from .settings import api_settings


def unset_jwt_cookies(response):
    cookie_name = api_settings.JWT_AUTH_COOKIE
    refresh_cookie_name = api_settings.JWT_AUTH_REFRESH_COOKIE
    refresh_cookie_path = api_settings.JWT_AUTH_REFRESH_COOKIE_PATH
    cookie_samesite = api_settings.JWT_AUTH_SAMESITE
    cookie_domain = api_settings.JWT_AUTH_COOKIE_DOMAIN

    if cookie_name:
        response.delete_cookie(
            cookie_name, samesite=cookie_samesite, domain=cookie_domain
        )
    if refresh_cookie_name:
        response.delete_cookie(
            refresh_cookie_name,
            path=refresh_cookie_path,
            samesite=cookie_samesite,
            domain=cookie_domain,
        )


def enforce_csrf(request):
    """
    Enforce CSRF validation for session based authentication.
    """

    def dummy_get_response(request):  # pragma: no cover
        return None

    check = CSRFCheck(dummy_get_response)
    # populates request.META['CSRF_COOKIE'], which is used in process_view()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        # CSRF failed, bail with explicit error message
        raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")
