from django.urls import path
from .views import (
    CreateBusinessWithUserAPIView,
    AllBusinessesAPIView,
    BusinessDetailAPIView,
    UpdateBusinessAPIView,
    DeleteBusinessAPIView,
    MyBusinessAPIView,
    ContactPersonListCreateAPIView,
    ContactPersonRetrieveUpdateDeleteAPIView,
    BranchLocationListCreateAPIView,
    BranchLocationRetrieveUpdateDeleteAPIView,
    GalleryListCreateAPIView,
    GalleryRetrieveUpdateDeleteAPIView,
    GalleryBulkUploadAPIView,
    ContactPersonChoicesAPIView,
    RecentlyViewedBusinessAPIView,
    SuperAdminDashboardAPIView,
    ExportBusinessesCSVAPIView,
    BusinessDashboardAPIView,
    IncreaseProfileViewAPIView,
<<<<<<< HEAD
    GalleryBulkUploadAPIView
=======
    RecentlyViewedBusinessAPIView,
    SuperAdminDashboardAPIView,
    ExportBusinessesCSVAPIView
>>>>>>> 3c0213fcf1aa38e8e989a8fbeed31282cccf65fa
)

app_name = 'business'

urlpatterns = [
    path('create-with-user/', CreateBusinessWithUserAPIView.as_view()),
    path('all/', AllBusinessesAPIView.as_view()),
    path('my/', MyBusinessAPIView.as_view()),
    path('<uuid:pk>/', BusinessDetailAPIView.as_view()),
    path('<uuid:pk>/update/', UpdateBusinessAPIView.as_view()),
    path('<uuid:pk>/delete/', DeleteBusinessAPIView.as_view()),
    path(
        'contact-person/choices/',
        ContactPersonChoicesAPIView.as_view(),
        name='contact-person-choices'
    ),
    path(
        'contact-persons/',
        ContactPersonListCreateAPIView.as_view(),
        name='contact-person-list-create'
    ),
    path(
        'contact-persons/<str:id>/',
        ContactPersonRetrieveUpdateDeleteAPIView.as_view(),
        name='contact-person-detail'
    ),
    path(
        'branch-locations/',
        BranchLocationListCreateAPIView.as_view(),
        name='branch-location-list-create'
    ),
    path(
        'branch-locations/<str:id>/',
        BranchLocationRetrieveUpdateDeleteAPIView.as_view(),
        name='branch-location-detail'
    ),
    path(
        'gallery/images/',
        GalleryListCreateAPIView.as_view(),
        name='gallery-image-list-create'
    ),
    path(
        'gallery/bulk-upload/',
        GalleryBulkUploadAPIView.as_view(),
        name='gallery-bulk-upload'
    ),
    path(
        "gallery/upload/<str:business_id>/",
        GalleryBulkUploadAPIView.as_view()
    ),
    path(
        'gallery/images/<str:id>/',
        GalleryRetrieveUpdateDeleteAPIView.as_view(),
        name='gallery-detail'
    ),
    path(
        '<str:business_id>/increase-view/',
        IncreaseProfileViewAPIView.as_view(),
        name='increase-profile-view'
    ),
    path(
        'recently-viewed/',
        RecentlyViewedBusinessAPIView.as_view(),
        name='recently-viewed-business'
    ),
    path(
        'admin/dashboard/',
        SuperAdminDashboardAPIView.as_view(),
        name='superadmin-dashboard'
    ),
    path(
        'export/csv/',
        ExportBusinessesCSVAPIView.as_view(),
        name='export-businesses-csv'
    ),
    path(
        'dashboard/',
        BusinessDashboardAPIView.as_view(),
        name='business-dashboard'
    ),
 
]
