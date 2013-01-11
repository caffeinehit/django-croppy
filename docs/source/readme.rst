django-croppy |image0|
======================

``django-croppy`` enables creating custom crops of images by specifying
a name, coordinates, width and height of the crop.

``django-croppy`` provides a custom model field responsible for creating
and deleting crops. Crops are stored as serialized JSON data on the same
model as the image field via
`django-jsonfield <http://pypi.python.org/pypi/django-jsonfield/>`_.

``django-croppy`` is useful if you want to manually curate the crop size
and location instead of relying on generic cropping like
`django-imagekit <http://pypi.python.org/pypi/django-imagekit/>`_
provides.

``django-croppy`` makes use of image processors provided by
``django-imagekit``.

Usage
-----

First, create your model with a crop field. You can specify a custom
location where to save crops to with the ``upload_to`` parameter:

::

    from django.db import models
    from croppy.fields import CropField

    def upload_to(instance, image, crop_name):
        filename, ext = os.path.splitext(os.path.split(image.name)[-1])
        return os.path.join('crops', '{}-{}{}'.format(filename, crop_name, ext))

    class Image(models.Model):
        image = models.ImageField()
        crops = CropField(upload_to = upload_to)

The created ``crops`` field allows you to create, delete and inspect
crops.

::

    $ cd tests && source test.sh && django-admin.py syncdb --settings tests.settings
    ...
    $ django-admin.py shell --settings tests.settings
    ...
    >>> from tests.app import tests
    >>> image = tests.get_image('test.tiff')
    >>> image
    <Image: Image object>
    >>> image.image
    <ImageFieldFile: images/test.tiff>
    >>> image.image.path
    u'/home/alen/projects/django-croppy/tests/test-media/images/test.tiff'

    >>> # Inspect the crop data
    >>> image.crops.data
    {}

    >>> # Create a new crop called 'rect' at position 0/0
    >>> # with a width of 100px and a height of 50px
    >>> image.crops.create('rect', (0, 0, 100, 50))

    >>> # Inspect the crop data
    >>> image.crops.data
    {'rect': {'y': 0, 'width': 100, 'height': 50, 'filename': 'crops/test-rect.tiff', 'x': 0}}

    >>> # Inspect the crop
    >>> image.crops.rect.name
    'crops/test-rect.tiff'
    >>> image.crops.rect.path
    u'/home/alen/projects/django-croppy/tests/test-media/crops/test-rect.tiff'
    >>> image.crops.rect.url
    '/test-media/crops/test-rect.tiff'

    >>> # Save the data to database 
    >>> image.save()

    >>> # Delete the crop
    >>> image.crops.delete('rect')
    >>> image.crops.data
    {}

.. |image0| image:: https://api.travis-ci.org/caffeinehit/django-croppy.png
