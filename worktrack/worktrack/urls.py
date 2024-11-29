from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core'), name='core'),
    path('api/schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='api_schema'), name='api_docs'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_swagger'),
]
