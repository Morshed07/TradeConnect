import uuid
from django.db import models
from django.core.validators import FileExtensionValidator


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Country(BaseModel):
    name = models.CharField(max_length=155, null=True, blank=True)
    flag = models.FileField(
        upload_to='country_flags/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['svg', 'png', 'jpg', 'jpeg'])]
    )

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

        ordering = ['name']

    def __str__(self):
        return self.name


class Service(BaseModel):
    title = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title
    

class Certification(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'

    def __str__(self):
        return self.name
