from rest_framework.authentication import TokenAuthentication as BaseTokenAuth

from users.models import UserAccount
from tokens.models import AuthToken
from helpers.logging import log_exception



class AuthTokenAuthentication(BaseTokenAuth):
    """
    Custom authentication class for token based authentication with token keyword as `AuthToken`.

    Example:
    ```
    Authorization: "AuthToken 5s45d6fugiohjklwrestrdytfuygiuhj"
    ```
    """
    model = AuthToken
    keyword = "AuthToken"



def universal_logout(user: UserAccount) -> bool:
    """
    Logs out the user from all devices by deleting auth token associated with the user.

    :param user: The user to log out.
    :return: True if the user was successfully logged out, False otherwise.
    """
    try:
        user.auth_token.delete()
    except Exception as exc:
        log_exception(exc)
        return False
    return True
