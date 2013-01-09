from django.db import models
from croppy.fields import CropsField

# Create your models here.


class Image(models.Model):
    image = models.ImageField(upload_to = 'images')
    crops = CropsField('image')

