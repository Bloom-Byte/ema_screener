from typing import Any
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


from . import permissions as perms
from . import authentication as auth



class AuthenticationRequired:
    """Permission mixin that requires the request user to be authenticated"""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.permission_classes = (*self.permission_classes, IsAuthenticated)
        self.authentication_classes = (*self.authentication_classes, auth.AuthTokenAuthentication)



class AuthenticationRequiredOrReadOnly:
    """Permission mixin that requires the request user to be authenticated or only allows read access"""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.permission_classes = (*self.permission_classes, IsAuthenticatedOrReadOnly)
        self.authentication_classes = (*self.authentication_classes, auth.AuthTokenAuthentication)



class RequiresAPIKey:
    """Permission mixin that requires the request user to provide an API key"""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.permission_classes = (*self.permission_classes, perms.HasAPIKey)

