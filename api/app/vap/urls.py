from django.contrib import admin
from django.urls import path, include
from drf_auto_endpoint.router import router
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import urls as rest_framework_urls
from importer import urls as importer_urls
from config import urls as config_urls
from core.endpoints import SearchViewSet

default_router = DefaultRouter()
default_router.register(r'search', SearchViewSet, basename='search')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/api', include(rest_framework_urls)),
    path('auth/token/', obtain_jwt_token),
    path('auth/refresh/', refresh_jwt_token),
    path('api/', include(router.urls)),
    path('api/', include(default_router.urls)),
    path('api/import/', include(importer_urls)),
    path('api/config/', include(config_urls)),
]
