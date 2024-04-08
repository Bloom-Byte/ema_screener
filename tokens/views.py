from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import response, status

from .models import AuthToken



class AuthTokenAuthenticationAPIView(ObtainAuthToken):
    """API view for authenticating users and generating tokens"""

    def get_response_data(self, user, token: AuthToken) -> dict:
        """
        Returns the response data for a successful authentication.
        Override this method to return custom data.
        By default, it returns the token key and user pk.

        :param user: The authenticated user
        :param token: The authentication token
        :return: The response data
        """
        return {
            'token': token.key,
            'user_id': user.pk,
        }
    

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = AuthToken.objects.get_or_create(user=user)
        data = self.get_response_data(user, token)
        return response.Response(data=data, status=status.HTTP_200_OK)
