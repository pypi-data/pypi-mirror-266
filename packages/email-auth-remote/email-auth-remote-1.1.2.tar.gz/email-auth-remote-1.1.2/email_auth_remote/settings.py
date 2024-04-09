from django.conf import settings
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, "EMAIL_AUTH_REMOTE", None)

DEFAULTS = {
    "JWT_AUTH_COOKIE": None,
    "JWT_AUTH_REFRESH_COOKIE": None,
    "JWT_AUTH_REFRESH_COOKIE_PATH": "/",
    "JWT_AUTH_COOKIE_USE_CSRF": False,
    "JWT_AUTH_COOKIE_ENFORCE_CSRF_ON_UNAUTHENTICATED": False,
    "JWT_AUTH_SECURE": False,
    "JWT_AUTH_HTTPONLY": True,
    "JWT_AUTH_SAMESITE": "Lax",
    "JWT_AUTH_COOKIE_DOMAIN": None,
    "JWT_REFRESH_URL": None,
    "ADMIN_LOGIN_URL": None,
    "LOGOUT_URL": None,
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = ()

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
