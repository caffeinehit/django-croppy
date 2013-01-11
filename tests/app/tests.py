from .models import Image
from croppy.fields import CropFieldDescriptor, CropFieldFile
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
import os
import shutil

def get_image(filename):
    path = os.path.join(
        os.path.dirname(__file__),
        'assets',
        filename)

    image = Image()

    with open(path) as f:
        image.image.save(filename, File(f))

    return image
                   
class CropsFieldTest(TestCase):
    def setUp(self):
        settings.DEBUG = True
        self.image = get_image('test.tiff')
        self.crop = (0, 0, 100, 100)

    def test_save_image(self):
        image = Image.objects.get(id=self.image.id)
        self.assertTrue(os.path.isfile(self.image.image.path))

    def test_field_setup(self):
        self.assertIsInstance(self.image.crops, CropFieldDescriptor)
        
    def test_create_crop(self):
        self.image.crops.create('square', self.crop)
            
        self.assertTrue(os.path.exists(self.image.crops.square.path))
        
        # Make sure it saved
        image = Image.objects.get(id=self.image.id)
        self.assertTrue(os.path.exists(image.crops.square.path))
        
        # Make sure it does not save with save=False
        with self.assertNumQueries(0):
            self.image.crops.create('rect', self.crop, save=False)

        image = Image.objects.get(pk=self.image.pk)

        self.assertFalse('rect' in image.crops.data)


    def test_delete_crop(self):
        self.image.crops.create('square', self.crop)
        path = self.image.crops.square.path 
                                            
        self.image.crops.delete('square')

        self.assertFalse('square' in self.image.crops.data)
        self.assertFalse(os.path.exists(path))

        # Make sure it saved
        image = Image.objects.get(id=self.image.id)
        self.assertFalse('square' in self.image.crops.data)

        # Make sure it does not save with save=False
        self.image.crops.create('square', self.crop)
        path = self.image.crops.square.path 
        
        self.image.crops.delete('square', save=False)
        
        image = Image.objects.get(id=self.image.id)
        
        self.assertFalse(os.path.exists(path))
        self.assertTrue('square' in image.crops.data)

    def test_create_and_load_crops(self):
        self.image.crops.create('square', self.crop)
        self.image.crops.create('rect', self.crop)
        
        image = Image.objects.get(id=self.image.id)
        
        self.assertIsInstance(image.crops.square, CropFieldFile)
        self.assertIsInstance(image.crops.rect, CropFieldFile)

        self.assertTrue(os.path.exists(image.crops.square.path))
        self.assertTrue(os.path.exists(image.crops.rect.path))

    def test_method_interference(self):
        """ Make sure that we can't use names for crops of methods already 
        present on the ``CropsDescriptor``. """
        
        try:
            self.assertRaises(ValidationError, lambda: self.image.crops.create('data',
                self.crop))
        except ValueError:
            import pdb;pdb.set_trace()
            self.assertRaises(ValidationError, lambda: self.image.crops.create('data',
                self.crop))
            
        def assign():
            self.image.crops.data = {
                'data': {'x': 0, 'y': 0,
                    'width': 100, 'height': 100,
                    'filename': 'data.tiff'}}
        
        self.assertRaises(ValidationError, assign)
        

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
