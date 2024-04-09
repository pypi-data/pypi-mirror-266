from drf_spectacular.contrib.rest_auth import SimpleJWTCookieScheme


class SimpleJWTTokenUserScheme(SimpleJWTCookieScheme):
    target_class = "email_auth_remote.authentication.JWTStatelessCookieAuthentication"
