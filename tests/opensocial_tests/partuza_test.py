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


__author__ = 'kurrik@google.com (Arne Roomann-Kurrik)'


import unittest
import urllib2

import opensocial

from opensocial import oauth
from opensocial import request


class TestPartuza(unittest.TestCase):
  
  def setUp(self):
    self.config = opensocial.ContainerConfig(      
        oauth_consumer_key='e2c2d2dd-e6c4-c4df-b2c4-d6efd2dcffd1',
        oauth_consumer_secret='eb214eedcda39f3440c43b623806912f',
        server_rpc_base='http://modules.partuza.nl/social/rpc',
        server_rest_base='http://modules.partuza.nl/social/rest',
        sign_with_body=True)
    self.container = opensocial.ContainerContext(self.config)
    self.user_id = '1311'

  def validate_user(self, user):
    self.assertEquals(self.user_id, user.get_id())
    
  def do_fetch_person(self, use_rpc, fields=None):
    self.container.set_allow_rpc(use_rpc)
    person = self.container.fetch_person(self.user_id, fields)
    return person
  
  def test_fetch_person_rpc(self):
    person = self.do_fetch_person(True)
    self.validate_user(person)

  def test_fetch_person_rest(self):
    person = self.do_fetch_person(False)
    self.validate_user(person)
        
  def test_fetch_person_fields_rpc(self):
    person = self.do_fetch_person(True, ['gender'])
    self.assertEquals('female', person.get_field('gender'))
    
  def test_fetch_person_fields_rest(self):
    person = self.do_fetch_person(False, ['gender'])
    self.assertEquals('female', person.get_field('gender'))
