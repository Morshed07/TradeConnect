from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import (
    CountrySerializer,
    ServiceSerializer,
    CertificationSerializer
)
from .models import (
    Country,
    Service,
    Certification
)
# Create your views here.


class CountryListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        countries = Country.objects.all()
        serializer = CountrySerializer(
            countries,
            many=True,
            context={'request': request}
        )
        return Response(
            {
                'success': True,
                'countries': serializer.data,
            },
            status=status.HTTP_200_OK
        )


class ServiceListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(
            {
                'success': True,
                'services': serializer.data
            },
            status=status.HTTP_200_OK
        )


class CertificationListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        certifications = Certification.objects.all()
        serializer = CertificationSerializer(certifications, many=True)
        return Response(
            {
                'success': True,
                'certifications': serializer.data
            },
            status=status.HTTP_200_OK
        )