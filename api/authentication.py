from django.http import HttpRequest
from rest_framework.authentication import TokenAuthentication as BaseTokenAuth


class AuthTokenAuthentication(BaseTokenAuth):
    """
    Custom authentication class for token based authentication with token keyword as `AuthToken`.

    Example:
    ```
    Authorization: "AuthToken 5s45d6fugiohjklwrestrdytfuygiuhj"
    ```
    """
    keyword = "AuthToken"


def universal_logout(request: HttpRequest) -> bool:
    """
    Logs out the user associated with the given request on all devices.

    :param request: The request object.
    :return: True if the user was successfully logged out, False otherwise.
    """
    if not request.user.is_authenticated:
        return False
    try:
        request.user.auth_token.delete()
    except Exception:
        return False
    return True
