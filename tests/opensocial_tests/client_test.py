
import unittest
import mock_http
import opensocial

from opensocial import simplejson
from opensocial import test_data
from opensocial.client import *

class TestRestRequest(unittest.TestCase):

  def setUp(self):
    self.config = ContainerConfig(server_rest_base='http://www.foo.com/rest/')

  def test_make_http_request(self):
    rest_request = RestRequest('@me/@friends')
    http_request = rest_request.make_http_request(self.config)
    self.assert_(http_request.method == 'GET')
    self.assert_(http_request.url.base ==
                 'http://www.foo.com/rest/@me/@friends')

    
class TestRpcRequest(unittest.TestCase):

  def setUp(self):
    self.config = ContainerConfig(server_rpc_base='http://www.foo.com/rpc')
  
  def test_make_http_request(self):
    rpc_request = RpcRequest('people.get', params={'userId': '101',
                                                   'groupId': '@friends'})
    http_request = rpc_request.make_http_request(self.config)
    self.assert_(http_request.method == 'POST')
    self.assert_(http_request.url.base == 'http://www.foo.com/rpc')
    json_body = {
      'params': {'userId': '101', 'groupId': '@friends'},
      'method': 'people.get',
    }
    post_body = simplejson.dumps(json_body)
    self.assert_(http_request.post_body == post_body)


class TestContainerContext(unittest.TestCase):

  viewer_response = http.Response(200, simplejson.dumps(
      {'entry': test_data.VIEWER_FIELDS}))

  friends_response = http.Response(200, simplejson.dumps(
      {'startIndex': 0,
       'totalResults': len(test_data.FRIEND_COLLECTION_FIELDS),
       'entry': test_data.FRIEND_COLLECTION_FIELDS}))

  noauth_response = http.Response(200, simplejson.dumps(test_data.NO_AUTH))

  def setUp(self):
    self.config = ContainerConfig(server_rest_base='http://www.foo.com/rest/')
    self.urlfetch = mock_http.MockUrlFetch()
    self.container = ContainerContext(self.config, self.urlfetch)

    self.urlfetch.add_response(
        http.Request(http.Url('http://www.foo.com/rest/people/@me/@self')),
        TestContainerContext.viewer_response)

    self.urlfetch.add_response(
        http.Request(http.Url('http://www.foo.com/rest/people/@me/@friends')),
        TestContainerContext.friends_response)

    self.urlfetch.add_response(
        http.Request(http.Url('http://www.foo.com/rest/people/102/@friends')),
        TestContainerContext.noauth_response)

    self.urlfetch.add_response(
        http.Request(http.Url('http://www.foo.com/rest/people/103/@friends')),
        http.Response(404, 'Error'))

  def test_supports_rpc(self):
    self.assertEqual(False, self.container.supports_rpc())
    
  def test_rest_request(self):
    request = self.container._create_rest_request(('foo', 'bar'))
    self.assertEqual('foo/bar', request.path)
    
  def test_rpc_request(self):
    request = self.container._create_rpc_request('people.get')
    self.assertEqual('people.get', request.params.get('method'))
    params = {'userId': '@me', 'groupId': '@friends'}
    request = self.container._create_rpc_request('people.get', params)
    args = request.params.get('params')
    self.assertEqual('@me', args.get('userId'))
    self.assertEqual('@friends', args.get('groupId'))

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
