"""vdp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_auto_endpoint.router import router
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import urls as rest_framework_urls

from core.models import Variant, Gene, VariantConsequence, Transcript

router.register(Variant)
router.register(Gene)
router.register(VariantConsequence)
router.register(Transcript)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/api', include(rest_framework_urls)),
    path('auth/token/', obtain_jwt_token),
    path('auth/refresh/', refresh_jwt_token),
    path('api/', include(router.urls)),
]
