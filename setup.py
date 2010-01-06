#!/usr/bin/python
#
# Copyright (C) 2007, 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'davidbyttow@google.com (David Byttow)'


from distutils.core import setup

setup(
    name='opensocial.py',
    version='DEVELOPMENT',
    description='Python client library for OpenSocial data APIs',
    author='David Byttow',
    author_email='davidbyttow@google.com',
    license='Apache 2.0',
    url='http://code.google.com/p/opensocial-python-client',
    packages=['opensocial', 'oauth', 'simplejson', 'Crypto', \
              'Crypto.PublicKey', 'Crypto.Util'],
    package_dir={'opensocial': 'src/opensocial',
                 'oauth': 'src/opensocial/oauth',
                 'simplejson': 'src/opensocial/simplejson',
                 'Crypto': 'src/opensocial/Crypto',}
)
