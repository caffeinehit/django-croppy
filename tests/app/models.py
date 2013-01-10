from croppy.fields import CropField
from django.db import models
from django.db.models.signals import pre_save

# Create your models here.


class Image(models.Model):
    image = models.ImageField(upload_to='images')
    crops = CropField('image')
    datetime = models.DateTimeField(auto_now=True)

