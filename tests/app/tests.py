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
        self.rect = (100, 100, 200, 100)

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
            self.image.crops.create('rect', self.rect, save=False)

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
        self.image.crops.create('rect', self.rect)
        
        image = Image.objects.get(id=self.image.id)
        
        self.assertIsInstance(image.crops.square, CropFieldFile)
        self.assertIsInstance(image.crops.rect, CropFieldFile)

        self.assertTrue(os.path.exists(image.crops.square.path))
        self.assertTrue(os.path.exists(image.crops.rect.path))

    def test_method_interference(self):
        """ Make sure that we can't use names for crops of methods already 
        present on the ``CropsDescriptor``. """
        
        self.assertRaises(ValidationError, lambda: self.image.crops.create('data',
            self.crop))
            
        def assign():
            self.image.crops.data = {
                'data': {'x': 0, 'y': 0,
                    'width': 100, 'height': 100,
                    'filename': 'data.tiff'}}
        
        self.assertRaises(ValidationError, assign)
        
    def test_iterator_and_length(self):
        self.image.crops.create('square', self.crop)
        self.image.crops.create('rect', self.rect)
        
        num = 0
        for crop in self.image.crops:
            self.assertTrue(os.path.exists(crop.path))
            num += 1

        self.assertEqual(2, num)
        
        self.assertEqual(2, len(self.image.crops))

    def test_resizing_crop(self):
        self.image.crops.create('square', self.crop)
        self.assertEqual(100, self.image.crops.square.width)
        self.assertEqual(100, self.image.crops.square.height)
        
        self.image.crops.create('resized_square', self.crop, resize=(200, 200))
        self.assertEqual(200, self.image.crops.resized_square.width)
        self.assertEqual(200, self.image.crops.resized_square.height)

    def test_clearing_all_crops(self):
        self.image.crops.create('square', self.crop)
        self.image.crops.create('rect', self.rect)

        square = self.image.crops.square.path 
        rect = self.image.crops.rect.path

        self.image.crops.clear()

        self.assertFalse(os.path.exists(square))
        self.assertFalse(os.path.exists(rect))

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        settings.DEBUG = False
