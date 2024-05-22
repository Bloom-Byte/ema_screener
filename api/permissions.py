from rest_framework_api_key.permissions import HasAPIKey as BaseHasAPIKey



class HasAPIKey(BaseHasAPIKey):
    """Permits only requests made a valid API key"""
    message = "Unauthorized request!"



