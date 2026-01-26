from rest_framework.views import APIView
from rest_framework.generics import (
    get_object_or_404,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import csv
from .models import (
    BusinessProfile,
    Gallery,
    ContactPerson,
    BranchLocation,
    RecentlyViewedBusiness
)
from .serializers import (
    BusinessProfileSerializer,
    CreateBusinessWithUserSerializer,
    UpdateBusinessProfileSerializer,
    ContactPersonSerializer,
    BranchLocationSerializer,
    GallerySerializer,
    GalleryBulkUploadSerializer,
    BusinessDashboardSerializer,
    RecentlyViewedBusinessSerializer,
    ContactPersonChoiceSerializer
)
from apps.account.permissions import IsSuperAdmin
from .permissions import IsSuperAdminOrOwner
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

User = get_user_model()


#  NEW PAGINATION CLASS
class BusinessPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateBusinessWithUserAPIView(APIView):
    permission_classes = [IsSuperAdmin]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        serializer = CreateBusinessWithUserSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            business = serializer.save()

            return Response({
                'success': True,
                'message': 'User and Business created successfully',
                'business': BusinessProfileSerializer(
                    business,
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class AllBusinessesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            businesses = BusinessProfile.objects.all()
        else:
            businesses = BusinessProfile.objects.filter(is_locked=False)

        country = request.query_params.get('country')
        if country:
            businesses = businesses.filter(country__name__icontains=country)

        search = request.query_params.get('search')
        if search:
            businesses = businesses.filter(business_name__icontains=search)

        service = request.query_params.get('service')
        if service:
            businesses = businesses.filter(service__title__icontains=service)

        sort_by = request.query_params.get('sort_by', '-created_at')

        allowed_sorts = {
            'a-z': 'business_name',
            'A-Z': 'business_name',
            'Newest': '-created_at',
            'newest': '-created_at',
        }

        if sort_by in allowed_sorts:
            businesses = businesses.order_by(allowed_sorts[sort_by])
        else:
            businesses = businesses.order_by('-created_at')
        
        status = request.query_params.get('status')
        if status == 'locked':
            businesses = businesses.filter(is_locked=True)
        elif status == 'active':
            businesses = businesses.filter(is_locked=False)
 
        # ========== PAGINATE ==========

        status = request.query_params.get('status')
        if status == 'locked':
            businesses = businesses.filter(is_locked=True)
        elif status == 'active':
            businesses = businesses.filter(is_locked=False)

        # ========== PAGINATE ==========

        paginator = BusinessPagination()
        paginated_businesses = paginator.paginate_queryset(businesses, request)

        # ========== SERIALIZE ==========
        serializer = BusinessProfileSerializer(
            paginated_businesses,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response({
            'success': True,
            'count': businesses.count(),
            'businesses': serializer.data
        })


class BusinessDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # 1️⃣ Get business or 404
        business = get_object_or_404(
            BusinessProfile.objects.select_related('user', 'country'),
            pk=pk
        )

        # 2️⃣ Permission check (ONLY if this is a private endpoint)
        # Remove this block if businesses are publicly viewable
        # if not request.user.is_superuser and business.user != request.user:
        #     return Response(
        #         {'success': False, 'message': 'Permission denied'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        # 3️⃣ Track recently viewed (safe)
        RecentlyViewedBusiness.objects.update_or_create(
            user=request.user,
            business=business
        )

        # 4️⃣ Serialize response
        serializer = BusinessProfileSerializer(
            business,
            context={'request': request}
        )

        return Response({
            'success': True,
            'business': serializer.data
        }, status=status.HTTP_200_OK)


class UpdateBusinessAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrOwner]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self, pk):
        try:
            return BusinessProfile.objects.get(pk=pk)
        except BusinessProfile.DoesNotExist:
            return None

    def patch(self, request, pk):
        business = self.get_object(pk)
        if not business:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, business)

        serializer = UpdateBusinessProfileSerializer(
            business,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'business': BusinessProfileSerializer(
                    business,
                    context={'request': request}
                ).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteBusinessAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def delete(self, request, pk):
        try:
            business = BusinessProfile.objects.get(pk=pk)
            user = business.user

            business.delete()

            if request.query_params.get('delete_user') == 'true':
                user.delete()

            return Response({'success': True})
        except BusinessProfile.DoesNotExist:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


class MyBusinessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            business = BusinessProfile.objects.select_related('user', 'country').get(user=request.user)
            serializer = BusinessProfileSerializer(business, context={'request': request})
            return Response({'success': True, 'business': serializer.data})
        except BusinessProfile.DoesNotExist:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)

class ContactPersonChoicesAPIView(APIView):
    def get(self, request):
        serializer = ContactPersonChoiceSerializer()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContactPersonListCreateAPIView(ListCreateAPIView):
    serializer_class = ContactPersonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        return ContactPerson.objects.filter(
            business_profile=business
        )

    def perform_create(self, serializer):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        serializer.save(business_profile=business)


class ContactPersonRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ContactPersonSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        return ContactPerson.objects.filter(
            business_profile=business
        )

    def perform_destroy(self, instance):
        if instance.is_primary:
            raise ValidationError(
                "Primary contact person cannot be deleted."
            )
        instance.delete()


class BranchLocationListCreateAPIView(ListCreateAPIView):
    serializer_class = BranchLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        return BranchLocation.objects.filter(
            business_profile=business
        )

    def perform_create(self, serializer):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        serializer.save(business_profile=business)


class BranchLocationRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = BranchLocationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        return BranchLocation.objects.filter(
            business_profile=business
        )


class GalleryListCreateAPIView(ListCreateAPIView):
    serializer_class = GallerySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        return Gallery.objects.filter(
            business_profile=business
        )

    def perform_create(self, serializer):
        business = get_object_or_404(
            BusinessProfile,
            user=self.request.user
        )
        serializer.save(business_profile=business)


# class GalleryBulkUploadAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]  # <--- add this

#     def post(self, request, id=None):
#         serializer = GalleryBulkUploadSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         images = serializer.validated_data['images']
#         business = get_object_or_404(BusinessProfile, user=request.user)

#         for image in images:
#             Gallery.objects.create(business_profile=business, image=image)

#         return Response(
#             {"message": f"{len(images)} images uploaded successfully"},
#             status=status.HTTP_201_CREATED
#         )
class GalleryBulkUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
 
    def post(self, request, business_id=None):
        serializer = GalleryBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        images = serializer.validated_data['images']
 
        # 🔐 Superadmin logic
        if request.user.is_superuser:
            if not business_id:
                return Response(
                    {"error": "business_id is required for superadmin"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            business = get_object_or_404(BusinessProfile, id=business_id)
 
        # 👤 Normal authenticated user
        else:
            business = get_object_or_404(
                BusinessProfile,
                user=request.user
            )
 
        for image in images:
            Gallery.objects.create(
                business_profile=business,
                image=image
            )
 
        return Response(
            {
                "message": f"{len(images)} images uploaded successfully",
                "business_id": business.id
            },
            status=status.HTTP_201_CREATED
        )


class GalleryRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = GallerySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            business = get_object_or_404(
                BusinessProfile,
                user=self.request.user
            )
            return Gallery.objects.filter(
                business_profile=business
            )
        else:
            return Gallery.objects.all()
        return Gallery.objects.all()


class BusinessDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        business = get_object_or_404(
            BusinessProfile,
            user=request.user
        )

        serializer = BusinessDashboardSerializer(business)
        return Response({
            "success": True,
            "data": serializer.data
        })


class IncreaseProfileViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, business_id):
        BusinessProfile.objects.filter(
            id=business_id
        ).update(profile_views=F('profile_views') + 1)

        return Response({"success": True})
    

class RecentlyViewedBusinessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_businesses = RecentlyViewedBusiness.objects.filter(
            user=request.user
        ).select_related(
            'business',
            'business__country'
        ).prefetch_related(
            'business__service'
        )[:3]  # show last 3

        serializer = RecentlyViewedBusinessSerializer(
            recent_businesses,
            many=True,
            context={'request': request}
        )

        return Response({
            "success": True,
            "data": serializer.data
        })


class SuperAdminDashboardAPIView(APIView):
    permission_classes = [IsSuperAdmin]
 
    def get(self, request):
        now = timezone.now()
 
        total_businesses = BusinessProfile.objects.count()
        locked_businesses = BusinessProfile.objects.filter(is_locked=True).count()
        total_users = User.objects.count()
 
        active_last_24h = BusinessProfile.objects.filter(
            user__last_login__gte=now - timedelta(hours=24)
        ).count()
 
        new_this_week = BusinessProfile.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()
 
        # ✅ Metrics with UI config
        metrics = [
            {
                "id": 1,
                "key": "total_businesses",
                "number": total_businesses,
                "description": "Total Businesses",
                "iconName": "<LuBriefcaseBusiness />",
                "iconBackgroundColor": "#BFD7FD",
                "iconColor": "#2459B1"
            },
            {
                "id": 2,
                "key": "active_last_24h",
                "number": active_last_24h,
                "description": "Active in Last 24h",
                "iconName": "<LuActivity />",
                "iconBackgroundColor": "#BFFDBA",
                "iconColor": "#279300"
            },
            {
                "id": 3,
                "key": "new_this_week",
                "number": new_this_week,
                "description": "New This Week",
                "iconName": "<BsPlusSquare />",
                "iconBackgroundColor": "#DBBFFF",
                "iconColor": "#8A38F5"
            },
            {
                "id": 4,
                "key": "locked_accounts",
                "number": locked_businesses,
                "description": "Locked Accounts",
                "iconName": "<TbLockAccess />",
                "iconBackgroundColor": "#FFBFBF",
                "iconColor": "#B3261E"
            }
        ]
 
        # Chart data (unchanged)
        chart_data = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
 
            chart_data.append({
                "date": day.strftime("%d %b"),
                "Logins": User.objects.filter(
                    last_login__gte=start,
                    last_login__lt=end
                ).count(),
                "NewBusinesses": BusinessProfile.objects.filter(
                    created_at__gte=start,
                    created_at__lt=end
                ).count(),
            })
 
        latest_businesses = BusinessProfile.objects.select_related(
            'user', 'country'
        ).order_by('-created_at')[:5]
 
        latest_businesses_data = [
                {
                    "id": b.id,
                    "business_name": b.business_name,
                    "country": b.country.name if b.country else "N/A",
                    "last_login": (
                        b.user.last_login.strftime("%Y-%m-%d %H:%M")
                        if b.user.last_login else "Never"
                    ),
                    "logo": (
                        request.build_absolute_uri(b.logo.url)
                        if b.logo else None
                    ),
                    "status": "Active" if not b.is_locked else "Locked",
                }
                for b in latest_businesses
            ]
 
        return Response({
            "success": True,
            "data": {
                "metrics": metrics,
                "chart_data": chart_data,
                "latest_businesses": latest_businesses_data,
                "total_users": total_users
            }
        })
       
    
class ExportBusinessesCSVAPIView(APIView):
    permission_classes = [IsSuperAdmin]
 
    def get(self, request):
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="businesses_export.csv"'
 
        # Get all businesses with related data
        businesses = BusinessProfile.objects.select_related(
            'user', 'country'
        ).prefetch_related(
            'service', 'certifications', 'contact_persons', 'branch_locations'
        ).all()
 
        # Create CSV writer
        writer = csv.writer(response)
 
        # Write header row
        writer.writerow([
            'Business ID',
            'Business Name',
            'User Email',
            'Phone Number',
            'Country',
            'Address',
            'Website',
            'Services',
            'Certifications',
            'About Business',
            'Profile Views',
            'Is Locked',
            'Membership Valid Till',
            'Created At',
            'Updated At',
            'Contact Persons',
            'Branch Locations'
        ])
 
        # Write data rows
        for business in businesses:
            # Get related data
            services = ', '.join([s.title for s in business.service.all()])
            certifications = ', '.join([c.name for c in business.certifications.all()])
            contact_persons = ', '.join(
                [f"{cp.full_name} ({cp.get_role_display_name()})"
                 for cp in business.contact_persons.all()]
            )
            branch_locations = ', '.join(
                [f"{bl.full_name} - {bl.city}"
                 for bl in business.branch_locations.all()]
            )
 
            writer.writerow([
                str(business.id),
                business.business_name,
                business.user.email,
                business.phone_number,
                business.country.name if business.country else '',
                business.full_address,
                business.website,
                services,
                certifications,
                business.about_business,
                business.profile_views,
                'Yes' if business.is_locked else 'No',
                business.membership_valid_till.strftime("%d-%m-%y") if business.membership_valid_till else '',
                business.created_at.strftime("%d-%m-%y %H:%M:%S"),
                business.updated_at.strftime("%d-%m-%y %H:%M:%S"),
                contact_persons,
                branch_locations
            ])
 
        return response