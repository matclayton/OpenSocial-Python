#!/usr/bin/python
#
# Copyright 2008 Google Inc. All Rights Reserved.

from distutils.core import setup

setup(
    name='opensocial.py',
    version='0.1.0',
    description='Python client library for OpenSocial data APIs',
    author='David Byttow',
    author_email='davidbyttow@google.com',
    license='Apache 2.0',
    url='http://code.google.com/p/opensocial-python-client',
    packages=['opensocial', 'opensocial.client', 'opensocial.data',
              'opensocial.oauth'],
    package_dir={'opensocial': 'src/opensocial'}
)
