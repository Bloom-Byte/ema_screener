from rest_framework_api_key.permissions import HasAPIKey


class HasAPIKeyOrIsAuthenticated(HasAPIKey):
    """Custom permission class to allow API key or authenticated users"""
    def has_permission(self, request, view)-> bool:
        return super().has_permission(request, view) or (request.user and request.user.is_authenticated)
