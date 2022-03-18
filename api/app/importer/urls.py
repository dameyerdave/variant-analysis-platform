from django.urls import path
from .views import AddVepVariantView

urlpatterns = [
    path('vep/region/<region>', AddVepVariantView.as_view())
]
