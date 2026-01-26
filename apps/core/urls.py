from django.urls import path
from .views import (
    CountryListAPIView,
    ServiceListAPIView,
    CertificationListAPIView
)

urlpatterns = [
    path('countries/', CountryListAPIView.as_view(), name='country-list'),
    path('services/', ServiceListAPIView.as_view(), name='service-list'),
    path('certifications/', CertificationListAPIView.as_view(), name='certification-list'),
]