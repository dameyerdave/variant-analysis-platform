from django.contrib import admin
from django.urls import path, include
from drf_auto_endpoint.router import router
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from rest_framework import urls as rest_framework_urls
from importer import urls as importer_urls
from config import urls as config_urls
from core.endpoints import SearchViewSet
from core.views import Report
from django_otp.admin import OTPAdminSite

default_router = DefaultRouter()
default_router.register(r'search', SearchViewSet, basename='search')

# Uncomment the following line if you want to disable 2fa for the admin interface
admin.site.__class__ = OTPAdminSite

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/api/', include(rest_framework_urls)),
    path('api/auth/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/', include(default_router.urls)),
    path('api/import/', include(importer_urls)),
    path('api/config/', include(config_urls)),
    path('api/report/<format>', Report.as_view(), name='report')
]
