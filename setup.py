# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import croppy

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().split('\n')

setup(
    name='django-croppy',
    version=croppy.__version__,
    description='Image library for creating user-croppable media',
    long_description=readme,
    author='Alen Mujezinovic',
    author_email='me@kennethreitz.com',
    url='https://github.com/caffeinehit/django-ilib',
    license=license,
    install_requires=install_requires,
    packages=find_packages(exclude=('tests', 'docs'))
)

