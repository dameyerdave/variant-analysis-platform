from django.contrib import admin
from django.urls import path, include
from drf_auto_endpoint.router import router
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import urls as rest_framework_urls
from importer import urls as importer_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/api', include(rest_framework_urls)),
    path('auth/token/', obtain_jwt_token),
    path('auth/refresh/', refresh_jwt_token),
    path('api/', include(router.urls)),
    path('api/import/', include(importer_urls))
]
