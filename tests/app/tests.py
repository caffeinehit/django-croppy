"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.files import File
from django.test import TestCase

from .models import *

import os

def get_image(filename):
    path = os.path.join(
        os.path.dirname(__file__),
        'assets',
        filename)

    image = Image()

    with open(path) as f:
        image.image.save(filename, File(f))

    return image
                   


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class CropsFieldTest(TestCase):
    def setUp(self):
        self.image = get_image('test.tiff')
        self.crop = (0,0,100,100)

    def test_save_image(self):
        image = Image.objects.get(id = self.image.id)
        self.assertTrue(os.path.isfile(self.image.image.path))

    def test_create_crop(self):
        self.image.crops.create('square', self.crop)
        self.assertTrue(self.image.crops.square)
        #self.assertTrue(os.path.isfile(self.image.crops.square.path))

    # def test_delete_crop(self):
    #     self.test_create_crop()
    #     path = self.image.crops.square.path 
    #     self.image.crops.square.delete()
    #     self.assertRaises(AttributeError, lambda: self.image.crops.square.path)
    #     self.assertFalse(os.path.isfile(path))
        
        
