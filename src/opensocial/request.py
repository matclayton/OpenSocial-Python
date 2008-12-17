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


import md5
import random
import time

import data
import http

from opensocial import simplejson


def generate_uuid(*args):
  """Simple method for generating a unique identifier.
  
  Args: Any arguments used to help make this uuid more unique.
  
  Returns: A 128-bit hex identifier.

  """
  t = long(time.time() * 1000)
  r = long(random.random() * 1000000000000000L)
  a = random.random() * 1000000000000000L
  data = '%s %s %s %s' % (str(t), str(r), str(a), str(args))
  return md5.md5(data).hexdigest()


class Request(object):
  """Represents an OpenSocial request that can be processed via RPC or REST."""
  
  def __init__(self, rest_request, rpc_request):
    self.rest_request = rest_request
    self.rpc_request = rpc_request
    
  def make_rest_request(self, url_base):
    """Creates a RESTful HTTP request.
    
    Args:
      url_base: str The base REST URL.

    """
    return self.rest_request.make_http_request(url_base)
  
  def make_rpc_request(self, url_base):
    """Creates a RPC-based HTTP request.
    
    Args:
      url_base: str The base RPC URL.

    """
    return self.rpc_request.make_http_request(url_base)


class FetchPeopleRequest(Request):    
  """A request for handling fetching a collection of people."""
  
  def __init__(self, user_id, group_id, params={}, id=None):
    params.update({'userId': user_id,
                   'groupId': group_id})
    rest_request = RestRequestInfo('/'.join(('people', user_id, group_id)))
    rpc_request = RpcRequestInfo('people.get', params=params)
    super(FetchPeopleRequest, self).__init__(rest_request, rpc_request)
    
  def process_json(self, json):
    """Construct the appropriate OpenSocial object from a JSON dict.
    
    Args:
      json: dict The JSON structure.
      
    Returns: a Collection of Person objects.

    """
    return data.Collection.parse_json(json, data.Person)

    
class FetchPersonRequest(FetchPeopleRequest):
  """A request for handling fetching a single person by id."""

  def __init__(self, user_id, params={}, id=None):
    super(FetchPersonRequest, self).__init__(user_id, '@self', 
                                             params=params, id=id)

  def process_json(self, json):
    """Construct the appropriate OpenSocial object from a JSON dict.
    
    Args:
      json: dict The JSON structure.
      
    Returns: A Person object.

    """
    return data.Person.parse_json(json)
  

class RestRequestInfo(object):
  """Represents a pending REST request."""

  def __init__(self, path, method='GET', fields=None):
    self.method = method
    self.path = path
    self.fields = fields

  def make_http_request(self, url_base):
    """Generates a http.Request object for the UrlFetch interface.
    
    Args:
      url_base: str The base REST URL.
    
    Returns: The http.Request object.

    """
    url = url_base + self.path
    return http.Request(url, method=self.method)


class RpcRequestInfo(object):
  """Represents a pending RPC request."""

  def __init__(self, method, params, id=None):
    self.method = method
    self.params = params
    self.id = id
  
  def make_http_request(self, url_base):
    """Generates a http.Request object for the UrlFetch interface.
    
    Args:
      url_base: str The base RPC URL.
    
    Returns: The http.Request object.

    """
    if self.id is None:
      self.id = generate_uuid(url_base) 
    rpc_body = {
      'method': self.method,
      'params': self.params,
      'id': self.id,
    }
    json_body = rpc_body
    return http.Request(url_base, method='POST', post_body=json_body)


class RequestBatch(object):
  """This class will manage the batching of requests."""
  
  def __init__(self):
    self.requests = {}
    self.data = {}
  
  def add_request(self, key, request):
    """Adds a request to this batch.
    
    Args:
      key: str A unique key to pair with the result of this request.
      request: obj The request object.

    """
    self.requests[key] = request

  def get(self, key):
    """Get the result value for a given request key.
    
    Args:
      key: str The key to retrieve.

    """
    return self.data.get(key)

  def send(self, container):
    """Execute the batch with the specified container.
    
    Args:
      container: The container to execute this batch on.

    """
    container.send_request_batch(self, False)

  def _set_data(self, key, data):
    self.data[key] = data

