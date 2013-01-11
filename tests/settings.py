import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tester', 'test@example.com'),
)    

SECRET_KEY = 'secret'

MEDIA_ROOT = os.path.join(
    os.path.dirname(__file__),
    'test-media')

MEDIA_URL = '/test-media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    },
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'croppy',
    'tests.app',
]


