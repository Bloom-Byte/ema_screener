from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include("api.urls", namespace="api"))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_header = f"{settings.SITE_NAME or "Trend Catcher"} Admin"
admin.site.site_title = f"{settings.SITE_NAME or "Trend Catcher"} Admin"
admin.site.index_title = f"{settings.SITE_NAME or "Trend Catcher"} Admin"
