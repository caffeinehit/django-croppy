from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage
from django.db.models.fields import TextField
from django.db.models.fields.files import ImageFieldFile
from imagekit.generators import SpecFileGenerator
from imagekit.processors.crop import Crop
import jsonfield
import os


def upload_to(instance, filename, crop_name):
    """
    Default function to specify a location to save crops to.
    
    :param instance: The model instance this crop field belongs to.
    :param filename: The image's filename this crop field operates on.
    :param crop_name: The crop name used when :attr:`CropFieldDescriptor.crop` was 
        called.
    """
    filename, ext = os.path.splitext(os.path.split(filename)[-1])
    return os.path.join('crops', u'%s-%s%s' % (filename, crop_name, ext))

class CropFieldFile(ImageFieldFile):
    """
    :attr:`CropFieldFile` objects are attached to a model's crop descriptor for each 
    specified crop spec.
    """
       
    def delete(self, save=True):
        """
        Overriding delete method to not reset the model instance with an empty 
        field. This would override all our other crops and the JSON metadata.
        
        .. note:: This method should not be called directly, rather use 
            :attr:`CropFieldDescriptor.delete`.
        
        :param save: When true, the instance is saved to the database after 
            the crop was deleted.
        """
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)
        
        if save:
            self.instance.save()
        
        self._commited = False

class CropFieldDescriptor(object):
    """
    Crop descriptors are created by :attr:`CropField` and allow for creating, 
    inspecting and deleting crops.  
    """
    def __init__(self, instance, field, data):
        self.instance = instance
        self.field = field
        self.image = getattr(instance, field.image_field)
        
        self._data = {}
        self.data = data        

    def create(self, name, spec, save=True):
        """
        Create a new crop with the provided spec. For example the following code
        creates a crop of the original image starting at the X/Y coordinates of 
        0/0 and having a width of 100 pixels and a height of 150 pixels::
                                                                        
            >>> image.crops.create('thumbnail', (0, 0, 100, 150))
        
        :param name: Crop name. This must be unique and is also used to generate
            the filename.
        :param spec: 4-tuple containing ``(x, y, width, height)``
        :param save: Boolean, if specified the model is saved back to DB after the crop.
        """
        
        self.validate_name(name)
        (x, y, width, height) = spec
        spec = {name: dict(x=x, y=y, width=width, height=height)}
        
        processors = [Crop(**spec[name])]
        
        filename = self.get_filename(name)

        spec[name]['filename'] = filename

        generator = SpecFileGenerator(processors, storage=self.field.storage)
        
        generator.generate_file(filename, self.image)

        self.data = dict(self.data, **spec)
        
        if save:
            self.instance.save()

        
    def delete(self, name, save=True):
        """
        Delete the named crop. If save is specified, the model instance is saved
        after the deletion.

        :param name: Crop name
        :param save: Boolean, whether to save the model instance or not after 
            deleting the file.
        """
        crop = getattr(self, name)
        delattr(self, name)
        del self._data[name]
        crop.delete(save)
    
    def validate_name(self, name):
        """ 
        Makes sure that the crop name does not clash with any methods or 
        attributes on :attr:`CropFieldDescriptor`. 

        Raises :attr:`django.core.exceptions.ValidationError` in case there is 
        a clash.
        """
           
        if hasattr(self, name) and not isinstance(getattr(self, name), CropFieldFile):
            raise ValidationError(
                "Cannot override existing attribute '%s' with crop file." % name
            )       
    def get_filename(self, name):
        """
        Delegate filename creation to :attr:`field.upload_to`. 
        """
        return self.field.upload_to(self.instance, self.image.name, name)
    
    @property
    def data(self):
        """ 
        Return the raw picture data as a dictionary including path, coordinates, e.g.:
        
            >>> model.crops.data
            {
                'thumbnail': {
                    'x': 0, 'y': 0, 
                    'width': 100, 'height': 100,
                    'name': 'crops/image_thumbnail.png'
                }, 
                'skyscraper': {
                    'x': 0, 'y': 0,
                    'width': 100, height: 600,
                    'name': 'crops/image_skyscraper.png'
                }
            }
        
        """
        return self._data
    
    @data.setter
    def data(self, value):
        """ 
        Sets the data attribute and generates :attr:`CropFieldFiles`
        for convenience methods and attributes like :attr:`CropFieldFiles.delete`,
        :attr:`CropFieldFiles.url`, :attr:`CropFieldFiles.path`, etc.
        """
        for name, spec in value.iteritems():
            self.validate_name(name)
            self._data[name] = spec
            
            if hasattr(self, name):
                continue

            setattr(self, name, CropFieldFile(
                self.instance,
                self.field,
                spec['filename']))
        

class CropFieldCreator(object):
    """ 
    Instead of using a metaclass for our custom field, we kind of
    follow :attr:`django.db.fields.files` in how to set up custom field 
    attributes on model objects. 
    """ 
    
    def __init__(self, field):
        self.field = field    

    def __get__(self, instance, cls):
        if instance is None:
            return self.field
        return instance.__dict__[self.field.name]


    def __set__(self, instance, data):
        """ 
        Turn data from string into Python and store the CropFieldDescriptor
        on the instance 
        """ 
        instance.__dict__[self.field.name] = CropFieldDescriptor(instance, self.field,
            self.field.to_python(data))
                                       


class CropField(TextField):
    """
    Creates custom crops from a specified model field::
    
        class MyModel(models.Model):
            my_image = models.ImageField()
            my_crops = CropField('my_image')
                                            
    """
                                               
    def __init__(self, image_field, *args, **kwargs):
        """
        Custom field to generate crops of custom sizes in custom locations.
        
        :param image_field: The name of the image field this cropper operates on.
        :param storage: A custom storage backend to use.
        :param upload_to: A custom function to generate crop filenames. Must take
            three attributes, ``instance``, ``image`` and ``crop_name``. See
            :attr:`upload_to`.
        """
        self.image_field = image_field

        # Storage is required to make ImageFieldFile work
        self.storage = kwargs.pop('storage', DefaultStorage())
        self.upload_to = kwargs.pop('upload_to', upload_to)

        kwargs['editable'] = kwargs.get('editable', False)
        
        self.json_field = jsonfield.JSONField(*args, **kwargs)

        kwargs['default'] = self.json_field.default
                                                           
        super(CropField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(CropField, self).contribute_to_class(cls, name)
        setattr(cls, name, CropFieldCreator(self))

    def get_db_prep_value(self, value, **kwargs):
        return self.json_field.get_db_prep_value(value.data, **kwargs)

    def to_python(self, value):
        return self.json_field.to_python(value)




