from django.urls import path
from .views import (
    LoginAPIView,
    ProfileAPIView, ChangePasswordAPIView,
    AllUsersAPIView, UserDetailAPIView,
    SuperAdminChangeUserPasswordAPIView
)
from rest_framework_simplejwt.views import (
    TokenRefreshView
)

app_name = 'account'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('users/', AllUsersAPIView.as_view(), name='all_users'),
    # path('users/create/', CreateUserAPIView.as_view(), name='create_user'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user_detail'),
    path('super-admin/users/change-password/', SuperAdminChangeUserPasswordAPIView.as_view()),
]
