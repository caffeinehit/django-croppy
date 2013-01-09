#!/bin/bash

export PYTHONPATH=$PWD/../:$PYTHONPATH

django-admin.py test app --settings tests.settings
