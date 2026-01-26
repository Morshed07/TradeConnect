
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'profile_image', 'is_business', 'is_staff', 'phone_number',
            'is_superuser', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']
        
    # def get_profile_image_url(self, obj):
    #     if obj.profile_image:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(obj.profile_image.url)
    #     return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email', '').lower()
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password required")
        
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_active:
            raise serializers.ValidationError("Account disabled")
        
        data['user'] = user
        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'profile_image', 'phone_number']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords don't match"
            })
        return data


class SuperAdminChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)  # user email
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })

        # Validate password strength
        validate_password(data['new_password'])
        return data

# class UserCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)

#     class Meta:
#         model = User
#         fields = (
#             'email',
#             'full_name',
#             'password',
#             'confirm_password',
#             'is_business',
#             'is_staff',
#             'is_superuser',
#         )

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError({
#                 'confirm_password': "Passwords do not match"
#             })
#         return data

#     def create(self, validated_data):
#         validated_data.pop('confirm_password')
#         password = validated_data.pop('password')

#         user = User.objects.create_user(
#             password=password,
#             **validated_data
#         )
#         return user
