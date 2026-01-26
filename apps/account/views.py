from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer, LoginSerializer,
    ProfileUpdateSerializer, ChangePasswordSerializer,
    # UserCreateSerializer
    SuperAdminChangePasswordSerializer
)
from .permissions import IsSuperAdmin
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.timezone import now

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        # ✅ Update last_login ONLY on successful login
        user.last_login = now()
        user.save(update_fields=['last_login'])

        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'Login successful',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': UserSerializer(
                user,
                context={'request': request}
            ).data
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                'success': True,
                'message': 'Logout successful'
            })
        except Exception:
            return Response({
                'success': False,
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response({
            'success': True,
            'user': serializer.data
        })

    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated',
                'user': UserSerializer(request.user, context={'request': request}).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'success': False,
                    'error': 'Old password incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)

            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# SUPER ADMIN ONLY
class AllUsersAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        users = User.objects.all().order_by('-created_at')

        is_business = request.query_params.get('is_business')
        if is_business is not None:
            users = users.filter(is_business=is_business.lower() == 'true')

        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response({
            'success': True,
            'count': users.count(),
            'users': serializer.data
        })


# class CreateUserAPIView(APIView):
#     permission_classes = [IsSuperAdmin]

#     def post(self, request):
#         serializer = UserCreateSerializer(data=request.data)

#         if serializer.is_valid():
#             user = serializer.save()
#             return Response({
#                 'success': True,
#                 'message': 'User created successfully',
#                 'user': UserSerializer(user, context={'request': request}).data
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             'success': False,
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    permission_classes = [IsSuperAdmin]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'user': UserSerializer(user, context={'request': request}).data
        })

    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'User updated',
                'user': UserSerializer(user, context={'request': request}).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        })


class SuperAdminChangeUserPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):  # no user_id, using email
        # Only superuser can do this
        if not request.user.is_superuser:
            return Response(
                {"error": "Only Super Admin can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SuperAdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data['email']  

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            "success": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.get_full_name() if hasattr(user, 'get_full_name') else ""
            },
            "message": f"Password updated for {user.email}"
        }, status=status.HTTP_200_OK) 