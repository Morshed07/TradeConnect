from django.contrib import admin
from .models import (
    BusinessProfile,
    ContactPerson,
    BranchLocation,
    Gallery
)

# Register your models here.

admin.site.register(BusinessProfile)
admin.site.register(ContactPerson)
admin.site.register(BranchLocation)
admin.site.register(Gallery)
