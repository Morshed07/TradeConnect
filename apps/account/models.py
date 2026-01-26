from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from apps.core.models import BaseModel


def user_image_upload_path(instance, filename):
    user_email = instance.email.replace("@", "_")
    return f"{user_email}/profile_image/{filename}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")    
        email = self.normalize_email(email).lower()

        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)

        if kwargs["is_staff"] is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs["is_superuser"] is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **kwargs)
    

class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to=user_image_upload_path, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    # Boolean to distinguish business users easily if needed later
    is_business = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
