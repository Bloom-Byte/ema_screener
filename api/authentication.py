from rest_framework.authentication import TokenAuthentication as BaseTokenAuth


class AuthTokenAuthentication(BaseTokenAuth):
    """Custom authentication class for token based authentication with token keyword as `AuthToken`."""
    keyword = "AuthToken"
