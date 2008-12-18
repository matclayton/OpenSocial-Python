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


import unittest

import opensocial


class TestOrkut(unittest.TestCase):
  
  def setUp(self):
    self.config = opensocial.ContainerConfig(
        oauth_consumer_key='orkut.com:623061448914',
        oauth_consumer_secret='uynAeXiWTisflWX99KU1D2q5',
        server_rest_base='http://sandbox.orkut.com/social/rest/')
    self.container = opensocial.ContainerContext(self.config)
    self.user_id = '03067092798963641994'

  def test_fetch_person(self):
    self.me = self.container.fetch_person(self.user_id)
    self.assertEquals(self.user_id, self.me.get_id())