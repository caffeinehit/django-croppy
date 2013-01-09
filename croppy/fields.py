from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageField, ImageFieldFile

import json
import jsonfield

class Crop(object):
    pass

class CropsDescriptor(object):
    def __init__(self, data):
        self.data = data
        self._post_init()

    def create(self, name, (x, y, width, height)):
        self._create_accessor(name, 'asdf')
        self.data[name] = 'asdf'

    def _post_init(self):
        for (key, value) in self.data.iteritems():
            self._create_accessor(key, value)

    def _create_accessor(self, name, value):
        setattr(self, name, Crop())
        

class CropsField(jsonfield.JSONField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, image_field, *args, **kwargs):
        self.image_field = image_field
        super(CropsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        data = super(CropsField, self).to_python(value)
        return CropsDescriptor(data)

    def get_db_prep_value(self, value, connection, prepared=False):
        return super(CropsField, self).get_db_prep_value(value.data, connection, prepared = False)
