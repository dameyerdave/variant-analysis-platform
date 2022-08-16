from django.urls import path
from users.views import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('auth/users', UserViewSet, basename='users')