from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    BusinessProfile,
    ContactPerson,
    BranchLocation,
    Gallery
)

@admin.register(BusinessProfile)
class BusinessProfileAdmin(ModelAdmin):
    pass

@admin.register(ContactPerson)
class ContactPersonAdmin(ModelAdmin):
    pass

@admin.register(BranchLocation)
class BranchLocationAdmin(ModelAdmin):
    pass

@admin.register(Gallery)
class GalleryAdmin(ModelAdmin):
    pass
