from django.db import models
from apps.account.models import User
from apps.core.models import BaseModel
from apps.core.models import (
    Country,
    Service,
    Certification
)
from django.core.validators import RegexValidator
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message="Enter a valid phone number"
)


class BusinessProfile(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='business_profile'
    )

    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator]
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_profiles'
    )

    full_address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)

    service = models.ManyToManyField(
        Service,
        related_name='business_profiles',
        blank=True
    )
    certifications = models.ManyToManyField(
        Certification,
        related_name='business_profiles',
        blank=True
    )
    about_business = models.TextField(blank=True)

    logo = models.ImageField(
        upload_to='business_logos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    is_locked = models.BooleanField(default=False)
    membership_valid_till = models.DateField(null=True, blank=True)
    profile_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.business_name

    class Meta:
        verbose_name = "Business Profile"
        verbose_name_plural = "Business Profiles"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['country']),
        ]


class ContactPerson(BaseModel):
    ROLE_CHOICES = [
        ('ceo', 'CEO'),
        ('managing_director', 'Managing Director'),
        ('operations_manager', 'Operations Manager'),
        ('sales_manager', 'Sales Manager'),
        ('business_development_manager', 'Business Development Manager'),
        ('account_manager', 'Account Manager'),
        ('customer_service_manager', 'Customer Service Manager'),
        ('general_manager', 'General Manager'),
        ('director', 'Director'),
        ('partner', 'Partner'),
        ('owner', 'Owner'),
        ('other', 'Other'),
    ]

    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='contact_persons'
    )

    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator]
    )

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        blank=True
    )

    # Custom role text (only used when role="other")
    custom_role = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_primary = models.BooleanField(default=False)

    def clean(self):
        if self.role == 'other' and not self.custom_role:
            raise ValidationError({
                'custom_role': 'Custom role is required when role is Other.'
            })

        if self.role != 'other' and self.custom_role:
            self.custom_role = None  # auto-clean

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_role_display_name(self):
        if self.role == 'other':
            return self.custom_role
        return self.get_role_display()

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display_name()})"

    class Meta:
        verbose_name = "Contact Person"
        verbose_name_plural = "Contact Persons"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business_profile']),
            models.Index(fields=['email']),
        ]


class BranchLocation(BaseModel):
    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='branch_locations'-
    )
    full_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='branch_locations'
    )
    phone_number = models.CharField(
            max_length=20,
            blank=True,
            validators=[phone_validator]
        )

    def __str__(self):
        return f"{self.full_name}, {self.address}, {self.city}"

    class Meta:
        verbose_name = "Branch Location"
        verbose_name_plural = "Branch Locations"
        indexes = [
            models.Index(fields=['business_profile']),
            models.Index(fields=['city']),
            models.Index(fields=['country']),
        ]


class Gallery(BaseModel):
    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='galleries'
    )
    image = models.ImageField(
        upload_to='business_galleries/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"Gallery Image for {self.business_profile.business_name}"

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
        indexes = [
            models.Index(fields=['business_profile']),
        ]


class RecentlyViewedBusiness(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recent_views'
    )
    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='viewed_by'
    )
    last_viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'business')
        ordering = ['-last_viewed_at']

    def __str__(self):
        return f"{self.user.email} → {self.business.business_name}"