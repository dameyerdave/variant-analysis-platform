""" 
We need to overwrite the default url patterns for the browseable API,
to support 2FA (with django_otp)
"""

from django.urls import path
from django.contrib.auth import views as django_auth_views
from django_otp import views as otp_views

app_name = 'rest_framework'
urlpatterns = [
    path('auth/api/login/',
         otp_views.LoginView.as_view(template_name='rest_framework/login.html'), name='login'),
    path('auth/api/logout/', django_auth_views.LogoutView.as_view(), name='logout'),
]
