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

import urllib
import httplib
import hashlib
import unittest
from base64 import b64encode

from opensocial import *
from opensocial import mock_http, simplejson, test_data


TEST_CONFIG = ContainerConfig(
    server_rest_base='http://www.foo.com/rest/',
)


class TestHttp(unittest.TestCase):
  
  def setUp(self):
    self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
    self.consumer = oauth.OAuthConsumer("consumer_key", "consumer_secret")

  def test_body_hash(self):
    post_body = "I am a post body"
    post_body_json = simplejson.dumps(post_body)
    post_body_hash = b64encode(hashlib.sha1(post_body_json).digest())
    post_body_param = simplejson.dumps(post_body)
    
    request = http.Request("http://example.com", "POST", post_body=post_body)
    request.set_body_as_signing_parameter(False)
    request.sign_request(self.consumer, self.signature_method)
    
    self.assertEquals(post_body_hash, request.get_parameter('oauth_body_hash'))
    headers = request.get_headers()
    self.assertEquals("application/json", headers['Content-Type'])
    
    try:
      request.get_parameter(post_body_param)
    except oauth.OAuthError:
      return
    self.fail()
    
  def test_body_as_signing_param(self):
    post_body = "I am a post body"
    post_body_param = simplejson.dumps(post_body)
    post_body_param_quoted = urllib.quote(post_body_param)
    
    request = http.Request("http://example.com", "POST", post_body=post_body)
    request.set_body_as_signing_parameter(True)
    request.sign_request(self.consumer, self.signature_method)
    
    param_location = request.get_url().find(post_body_param_quoted)
    self.assertTrue(param_location > -1)
    self.assertEquals("", request.get_parameter(post_body_param))
    
    try:
      request.get_parameter('oauth_body_hash')
    except oauth.OAuthError:
      return
    self.fail()
    
class TestRestRequest(unittest.TestCase):

  def test_http_request(self):
    rest_request = request.RestRequestInfo('@me/@friends')
    http_request = rest_request.make_http_request(TEST_CONFIG.server_rest_base)
    self.assertEquals('GET', http_request.get_method())
    self.assertEquals(
        'http://www.foo.com/rest/@me/@friends?opensocial_method=GET',
        http_request.get_url())

    
class TestRpcRequest(unittest.TestCase):

  def test_rpc_body(self):
    rpc_request = RpcRequestInfo('people.get',
                                 params={'userId': '101',
                                         'groupId': '@friends'},
                                 id='foo')
    rpc_body = rpc_request.get_rpc_body()
    self.assertEquals('people.get', rpc_body['method'])
    self.assertEquals('foo', rpc_body['id'])
    self.assertEquals('101', rpc_body['params']['userId'])
    self.assertEquals('@friends', rpc_body['params']['groupId'])

  def test_text_request(self):
    rpc_request = TextRpcRequest("""{
      "method": "people.get", 
      "id": "foo", 
      "params": { 
        "userId" : "101",
        "groupId" : "@friends"
      }
    }""");
    
    rpc_body = rpc_request.get_rpc_body()
    self.assertEquals('people.get', rpc_body['method'])
    self.assertEquals('foo', rpc_body['id'])
    self.assertEquals('101', rpc_body['params']['userId'])
    self.assertEquals('@friends', rpc_body['params']['groupId'])

class TestValidator(unittest.TestCase):
  def test_validate_rsa(self):
    public_key_str = ("0x00deb51922b2a31dfea37045540385be3b39343ff5b384e105" +
                      "339a78e534d13dacf7adad7c20117e180f5f25b702c8730794a0" +
                      "eaa6a9e69e37b53fad0a1fc6ffcb838a6d8592de2456aed90270" +
                      "87b4cea8df20f5ae7a00b758043708f0a9a2f68f4923d43e19ff" +
                      "e358872ad90700782fbb9a9acdbe207bdc35cddbe30e8fecb7d5")
    
    validator = RsaSha1Validator(public_key_str)

    url = "http://graargh.returnstrue.com/buh/fetchme.php"
    params = {
      'oauth_body_hash'            : '2jmj7l5rSw0yVb/vlWAYkK/YBwk=',
      'opensocial_owner_id'        : 'john.doe',
      'opensocial_viewer_id'       : 'john.doe',
      'opensocial_app_id'          : '3995',
      'opensocial_app_url'         : 'http://localhost/~kurrik/makeRequest.xml',
      'oauth_version'              : '1.0',
      'oauth_timestamp'            : '1255470195',
      'oauth_consumer_key'         : "kurrik",
      'oauth_signature_method'     : 'RSA-SHA1',
      'oauth_nonce'                : '1255470195040198000',
      'oauth_signature'            : 'mFxgSmrgYxo8GbJji/6pbjTVIEBoVC6tHHp9QSwORqiPg2I1mG7t6M100XVSowpMpxO76miKOTBxQmeCs26QmBQP1uf9U1yMHs5hqj3b+TbkyIQLflKl9A+WoGr2xFQoQ0i9S+Pq2L3CXS7pFuYqom2UbokixfjRAmtBztyLJQE=',
      'xoauth_public_key'          : 'openssl_key_pk8_shindig.pem',
      'xoauth_signature_publickey' : 'openssl_key_pk8_shindig.pem',
    }
    is_valid_request = validator.validate("GET", url, params)
    self.assertTrue(is_valid_request)
    
  def test_validate_invalid_rsa(self):
    # invalid public key
    public_key_str = ("0x00abc51922b2a31dfea37045540385be3b39343ff5b384e105" +
                      "339a78e534d13dacf7adad7c20117e180f5f25b702c8730794a0" +
                      "eaa6a9e69e37b53fad0a1fc6ffcb838a6d8592de2456aed90270" +
                      "87b4cea8df20f5ae7a00b758043708f0a9a2f68f4923d43e19ff" +
                      "e358872ad90700782fbb9a9acdbe207bdc35cddbe30e8fecb7d5")

    validator = RsaSha1Validator(public_key_str)

    url = "http://graargh.returnstrue.com/buh/fetchme.php"
    params = {
      'oauth_body_hash'            : '2jmj7l5rSw0yVb/vlWAYkK/YBwk=',
      'opensocial_owner_id'        : 'john.doe',
      'opensocial_viewer_id'       : 'john.doe',
      'opensocial_app_id'          : '3995',
      'opensocial_app_url'         : 'http://localhost/~kurrik/makeRequest.xml',
      'oauth_version'              : '1.0',
      'oauth_timestamp'            : '1255470195',
      'oauth_consumer_key'         : "kurrik",
      'oauth_signature_method'     : 'RSA-SHA1',
      'oauth_nonce'                : '1255470195040198000',
      'oauth_signature'            : 'mFxgSmrgYxo8GbJji/6pbjTVIEBoVC6tHHp9QSwORqiPg2I1mG7t6M100XVSowpMpxO76miKOTBxQmeCs26QmBQP1uf9U1yMHs5hqj3b+TbkyIQLflKl9A+WoGr2xFQoQ0i9S+Pq2L3CXS7pFuYqom2UbokixfjRAmtBztyLJQE=',
      'xoauth_public_key'          : 'openssl_key_pk8_shindig.pem',
      'xoauth_signature_publickey' : 'openssl_key_pk8_shindig.pem',
    }
    is_valid_request = validator.validate("GET", url, params)
    self.assertFalse(is_valid_request)
    
  def test_validate_hmac(self):
    validator = HmacSha1Validator("I'm a consumer secret!")
    
    url = "http://graargh.returnstrue.com/buh/fetchme.php"
    params = {
      'oauth_body_hash'        : '2jmj7l5rSw0yVb/vlWAYkK/YBwk=',
      'opensocial_owner_id'    : 'john.doe',
      'opensocial_viewer_id'   : 'john.doe',
      'opensocial_app_id'      : '3995',
      'opensocial_app_url'     : 'http://localhost/~kurrik/makeRequest.xml',
      'oauth_version'          : '1.0',
      'oauth_timestamp'        : '1255468709',
      'oauth_consumer_key'     : "I'm a consumer key!",
      'oauth_signature_method' : 'HMAC-SHA1',
      'oauth_nonce'            : '1255468709246019000',
      'oauth_signature'        : '0CoUIWCAaBtjJqW3wQ0DJXNEa+o=',
    }
    is_valid_request = validator.validate("GET", url, params)
    self.assertTrue(is_valid_request)
    
  def test_validate_invalid_hmac(self):
    # invalid consumer secret
    validator = HmacSha1Validator("I'm an incorrect consumer secret!")

    url = "http://graargh.returnstrue.com/buh/fetchme.php"
    params = {
      'oauth_body_hash'        : '2jmj7l5rSw0yVb/vlWAYkK/YBwk=',
      'opensocial_owner_id'    : 'john.doe',
      'opensocial_viewer_id'   : 'john.doe',
      'opensocial_app_id'      : '3995',
      'opensocial_app_url'     : 'http://localhost/~kurrik/makeRequest.xml',
      'oauth_version'          : '1.0',
      'oauth_timestamp'        : '1255468709',
      'oauth_consumer_key'     : "I'm a consumer key!",
      'oauth_signature_method' : 'HMAC-SHA1',
      'oauth_nonce'            : '1255468709246019000',
      'oauth_signature'        : '0CoUIWCAaBtjJqW3wQ0DJXNEa+o=',
    }
    is_valid_request = validator.validate("GET", url, params)
    self.assertFalse(is_valid_request)
    
class TestContainerContext(unittest.TestCase):

  friends_response = http.Response(httplib.OK, simplejson.dumps(
      test_data.FRIEND_COLLECTION_FIELDS))

  noauth_response = http.Response(httplib.OK,
                                  simplejson.dumps(test_data.NO_AUTH))

  def setUp(self):
    self.urlfetch = mock_http.MockUrlFetch()
    self.container = ContainerContext(TEST_CONFIG, self.urlfetch)

  def test_supports_rpc(self):
    self.assertEqual(False, self.container.supports_rpc())
    
  def test_fetch_person(self):
    response = http.Response(httplib.OK, simplejson.dumps({
      'entry': {
        'id' : '101',
        'name' : { 'givenName': 'Kenny', 'familyName': 'McCormick'}
      },
    }))
    self.urlfetch.add_response(response)
    
    person = self.container.fetch_person('@me')
    
    request = self.urlfetch.get_request()
    self.assertEqual('101', person.get_id())
    self.assertEqual('Kenny McCormick', person.get_display_name())
    self.assertEqual('http://www.foo.com/rest/people/@me/@self', 
                     request.get_normalized_url())

  def test_fetch_friends(self):
    response = http.Response(httplib.OK, simplejson.dumps({
      'startIndex': 0,
      'totalResults': 3,
      'entry': [
        { 
          'id': '102',
          'name': {'givenName': 'Stan', 'familyName': 'Marsh'},
        },
        { 
          'id': '103',
          'name': {'givenName': 'Kyle', 'familyName': 'Broflovski'},
        },
        { 
          'id': '104',
          'name': {'givenName': 'Eric', 'familyName': 'Cartman'},
        }
      ]
    }))
    self.urlfetch.add_response(response)
    
    friends = self.container.fetch_friends('@me')
    
    request = self.urlfetch.get_request()                     
    self.assertEqual(0, friends.startIndex)
    self.assertEqual(3, friends.totalResults)
    self.assertEqual('102', friends[0].get_id())
    self.assertEqual('Stan Marsh', friends[0].get_display_name())
    self.assertEqual('103', friends[1].get_id())
    self.assertEqual('Kyle Broflovski', friends[1].get_display_name())
    self.assertEqual('104', friends[2].get_id())
    self.assertEqual('Eric Cartman', friends[2].get_display_name())
    self.assertEqual('http://www.foo.com/rest/people/@me/@friends', 
                     request.get_normalized_url())
      
  def test_unauthorized_request(self):
    response = http.Response(httplib.OK, simplejson.dumps({
      'error' : { 'code': httplib.UNAUTHORIZED }
    }))
    self.urlfetch.add_response(response)
    
    self.assertRaises(UnauthorizedRequestError,
                      self.container.fetch_friends,
                      '102')
    
    request = self.urlfetch.get_request()
    self.assertEqual('102', request.get_parameter('xoauth_requestor_id'))
    self.assertEqual('http://www.foo.com/rest/people/102/@friends', 
                     request.get_normalized_url())

 
  def test_bad_request(self):
    response = http.Response(httplib.NOT_FOUND, 'Error');
    self.urlfetch.add_response(response)
    
    self.assertRaises(BadRequestError, self.container.fetch_friends, '103')
    
    request = self.urlfetch.get_request()
    self.assertEqual('103', request.get_parameter('xoauth_requestor_id'))
    self.assertEqual('http://www.foo.com/rest/people/103/@friends', 
                     request.get_normalized_url())
    