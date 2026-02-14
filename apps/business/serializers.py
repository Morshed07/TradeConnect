from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BusinessProfile, ContactPerson, BranchLocation, Gallery, RecentlyViewedBusiness
from apps.core.models import Country, Service, Certification
from apps.core.serializers import CountrySerializer

User = get_user_model()


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name']
        read_only_fields = ['id']


class ContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPerson
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'role',
            'custom_role',
            'is_primary',
        ]
        read_only_fields = ['id']


class BranchLocationSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = BranchLocation
        fields = [
            'id',
            'full_name',
            'address',
            'city',
            'country',
            'phone_number',
        ]
        read_only_fields = ['id']


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = [
            'id',
            'image',
        ]
        read_only_fields = ['id']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title']
        read_only_fields = ['id', 'title']


class BusinessProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    country = CountrySerializer(read_only=True)

    services = ServiceSerializer(
        source='service',
        many=True,
        read_only=True
    )
    branches = BranchLocationSerializer(
        source='branch_locations',
        many=True,
        read_only=True
    )
    contacts = ContactPersonSerializer(
        source='contact_persons',
        many=True,
        read_only=True
    )
  
    certifications = CertificationSerializer(
        many=True,
        read_only=True
    )

    gallery = GallerySerializer(
        source='galleries',
        many=True,
        read_only=True
    )
    membership_valid_till = serializers.DateField(
        format="%d/%m/%Y",
        required=False,
        allow_null=True
    )

    class Meta:
        model = BusinessProfile
        fields = [
            'id',
            'user_email',
            'user_full_name',
            'business_name',
            'phone_number',
            'country',
            'full_address',
            'website',
            'membership_valid_till',
            'services',
            'branches',
            'contacts',
            'certifications',
            'about_business',
            'logo',
            'gallery',
            'is_locked',
            'is_featured',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CreateBusinessWithUserSerializer(serializers.Serializer):
    # -------- USER --------
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True)

    # -------- BUSINESS --------
    business_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )
    full_address = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    membership_valid_till = serializers.DateField(
        required=False,
        allow_null=True,
        format='%d/%m/%Y',
        input_formats=['%d/%m/%Y', '%d/%m/%y']
    )

    # Change this to 'services' to match your request data
    services = serializers.CharField(required=False, allow_blank=True)
    about_business = serializers.CharField(required=False, allow_blank=True)
    certifications = serializers.PrimaryKeyRelatedField(
        queryset=Certification.objects.all(),
        many=True,
        required=False
    )
    # ✅ MUST exist
    logo = serializers.ImageField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value.lower()

    def create(self, validated_data):
        # Pop M2M fields FIRST
        services_raw = validated_data.pop('services', None)
        certifications = validated_data.pop('certifications', None)

        logo = validated_data.pop('logo', None)
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        full_name = validated_data.pop('full_name', '')
        membership_valid_till = validated_data.pop('membership_valid_till', None)

        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            profile_image=logo,
            is_business=True,
            is_superuser=False,
            is_staff=False
        )

        # Create business
        business = BusinessProfile.objects.create(
            user=user,
            logo=logo,
            membership_valid_till=membership_valid_till,
            **validated_data
        )

        # ✅ Handle certifications (same pattern as update)
        if certifications is not None:
            business.certifications.set(certifications)

        # ✅ Handle services
        if services_raw is not None:
            service_objects = []

            if services_raw:
                service_names = [
                    name.strip().title()
                    for name in services_raw.split(',')
                    if name.strip()
                ]

                for name in service_names:
                    service_obj, _ = Service.objects.get_or_create(title=name)
                    service_objects.append(service_obj)

            business.service.set(service_objects)

        return business


class UpdateBusinessProfileSerializer(serializers.ModelSerializer):
    services = serializers.CharField(required=False, allow_blank=True)
    membership_valid_till = serializers.DateField(
        required=False,
        allow_null=True,
        format='%d/%m/%Y',
        input_formats=['%d/%m/%Y', '%d/%m/%y']
    )
    certifications = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    class Meta:
        model = BusinessProfile
        fields = [
            'business_name',
            'phone_number',
            'country',
            'full_address',
            'website',
            'services',
            'certifications',
            'about_business',
            'membership_valid_till',
            'logo',
            'is_locked',
            'is_featured',
        ]

    def update(self, instance, validated_data):
        #  MUST pop M2M fields FIRST
        services_raw = validated_data.pop('services', None)
        certifications = validated_data.pop('certifications', None)
 
        # update normal fields only
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
 
        #  handle services (M2M via string)
        if services_raw is not None:
            service_objects = []
 
            if services_raw:
                service_names = [
                    name.strip().title()
                    for name in services_raw.split(',')
                    if name.strip()
                ]
 
                for name in service_names:
                    service_obj, _ = Service.objects.get_or_create(title=name)
                    service_objects.append(service_obj)
 
            instance.service.set(service_objects)
 
        #  handle certifications (M2M correct way)
        if certifications is not None:
            instance.certifications.set(certifications)
 
        instance.save()
        return instance


class ContactPersonChoiceSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return {
            "roles": [
                {
                    "value": key,
                    "label": label
                }
                for key, label in ContactPerson.ROLE_CHOICES
            ]
        }


class ContactPersonSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(
        source='get_role_display_name',
        read_only=True
    )
    class Meta:
        model = ContactPerson
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'role',
            'custom_role',
            'is_primary',
            'role_display',
        ]
        read_only_fields = ['id']


class BranchLocationSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = BranchLocation
        fields = [
            'id',
            'full_name',
            'address',
            'city',
            'country',
            'country_name',
            'phone_number',
        ]
        read_only_fields = ['id']


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = [
            'id',
            'image',
        ]
        read_only_fields = ['id']


class GalleryBulkUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        max_length=8
    )

    def validate_images(self, images):
        if len(images) > 8:
            raise serializers.ValidationError(
                "You can upload a maximum of 8 images."
            )
        return images


class BusinessDashboardSerializer(serializers.ModelSerializer):
    profile_completeness = serializers.SerializerMethodField()

    class Meta:
        model = BusinessProfile
        fields = [
            'profile_completeness',
            'membership_valid_till',
            'profile_views',
        ]

    def get_profile_completeness(self, obj):
        user = obj.user

        fields = [
            user.email,
            obj.business_name,
            obj.phone_number,
            obj.country,
            obj.full_address,
            obj.website,
            obj.about_business,
            obj.logo,
        ]

        many_to_many_fields = [
            obj.service.exists(),
            obj.certifications.exists(),
        ]

        total_fields = len(fields) + len(many_to_many_fields)
        filled_fields = sum(bool(field) for field in fields) + sum(many_to_many_fields)

        return round((filled_fields / total_fields) * 100)


class RecentViewedBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = [
            'id',
            'business_name',
        ]


class RecentlyViewedBusinessSerializer(serializers.ModelSerializer):
    business_name = RecentViewedBusinessSerializer(source='business')
    country = serializers.CharField(
        source='business.country.name',
        default=None
    )
    services = serializers.SerializerMethodField()
    logo = serializers.ImageField(
        source='business.logo'
    )

    class Meta:
        model = RecentlyViewedBusiness
        fields = [
            'business_name',
            'country',
            'services',
            'logo',
            'last_viewed_at',
        ]

    def get_services(self, obj):
        return list(
            obj.business.service.values_list('title', flat=True)
        )