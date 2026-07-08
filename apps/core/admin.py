from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Country, Service, Certification

@admin.register(Country)
class CountryAdmin(ModelAdmin):
    pass

@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    pass

@admin.register(Certification)
class CertificationAdmin(ModelAdmin):
    pass