from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def health_check_api_view(request, *args, **kwargs) -> JsonResponse:
    """Simple view to test if the API server is up and running."""
    return JsonResponse(
        data={
            "message": "Server is !down."
        },
        status=200
    )

