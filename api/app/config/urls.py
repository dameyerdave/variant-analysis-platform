from django.urls import path
from .views import ConfigView

urlpatterns = [
    path('', ConfigView.as_view()),
    path('<use_config>', ConfigView.as_view())
]