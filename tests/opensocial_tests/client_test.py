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

from opensocial import *
from opensocial import mock_http, simplejson, test_data


TEST_CONFIG = ContainerConfig(
    server_rest_base='http://www.foo.com/rest/')


class TestRestRequest(unittest.TestCase):

  def test_http_request(self):
    rest_request = request.RestRequestInfo('@me/@friends')
    http_request = rest_request.make_http_request(TEST_CONFIG.server_rest_base)
    self.assertEquals('GET', http_request.get_method())
    self.assertEquals('http://www.foo.com/rest/@me/@friends?',
                      http_request.get_url())

    
class TestRpcRequest(unittest.TestCase):

  def test_make_http_request(self):
    rpc_request = RpcRequestInfo('people.get',
                                params={'userId': '101',
                                        'groupId': '@friends'},
                                id='foo')
    http_request = rpc_request.make_http_request('http://www.foo.com/rpc')
    self.assertEquals('POST', http_request.get_method())
    self.assertEquals('http://www.foo.com/rpc?', http_request.get_url())
    json_body = {
      'params': {'userId': '101', 'groupId': '@friends'},
      'method': 'people.get',
      'id': 'foo',
    }
    post_body = simplejson.dumps(json_body)
    self.assertEquals(post_body, http_request.post_body)


class TestContainerContext(unittest.TestCase):

  viewer_response = http.Response(200, simplejson.dumps(
      {'entry': test_data.VIEWER_FIELDS}))

  friends_response = http.Response(200, simplejson.dumps(
      {'startIndex': 0,
       'totalResults': len(test_data.FRIEND_COLLECTION_FIELDS),
       'entry': test_data.FRIEND_COLLECTION_FIELDS}))

  noauth_response = http.Response(200, simplejson.dumps(test_data.NO_AUTH))

  def add_canned_response(self, request_url, http_response):
    http_request = http.Request(request_url)
    self.urlfetch.add_response(http_request, http_response)

  def setUp(self):
    self.urlfetch = mock_http.MockUrlFetch()
    self.container = ContainerContext(TEST_CONFIG, self.urlfetch)

    self.add_canned_response('http://www.foo.com/rest/people/@me/@self',
                             TestContainerContext.viewer_response)

    self.add_canned_response('http://www.foo.com/rest/people/@me/@friends',
                             TestContainerContext.friends_response)

    self.add_canned_response('http://www.foo.com/rest/people/102/@friends',
                             TestContainerContext.noauth_response)

    self.add_canned_response('http://www.foo.com/rest/people/103/@friends',
                              http.Response(404, 'Error'))

  def test_supports_rpc(self):
    self.assertEqual(False, self.container.supports_rpc())
    test_rpc = ContainerContext(ContainerConfig(server_rpc_base='test'))
    self.assertEqual(True, test_rpc.supports_rpc())
    
  def test_fetch_person(self):
    person = self.container.fetch_person('@me')
    self.assertEqual(test_data.VIEWER.get_id(), person.get_id())
    self.assertEqual(test_data.VIEWER.get_display_name(),
                     person.get_display_name())

  def test_fetch_friends(self):
    friends = self.container.fetch_friends('@me')
    self.assertEqual(friends.start, test_data.FRIEND_COLLECTION.start)
    self.assertEqual(friends.total, test_data.FRIEND_COLLECTION.total)
    for i in range(len(friends.items)):
      person = friends.items[i]
      test_person = test_data.FRIENDS[i]
      self.assertEqual(person.get_id(), test_person.get_id())
      self.assertEqual(person.get_display_name(), test_person.get_display_name())
      
  def test_unauthorized_request(self):
    self.assertRaises(UnauthorizedRequest, self.container.fetch_friends, '102')
 
  def test_bad_request(self):
    self.assertRaises(BadRequest, self.container.fetch_friends, '103')
    self.assertRaises(BadRequest, self.container.fetch_friends, '??')
