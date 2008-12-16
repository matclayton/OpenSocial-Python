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


import sys
import urllib

from opensocial import oauth
try:
  from google.appengine.api import urlfetch
except:
  pass


def get_default_urlfetch():
  """Creates the default UrlFetch interface.
  
  If AppEngine environment is detected, then the AppEngineUrlFetch object
  will be created.
  
  TODO: Find a better way to determine if this is an AppEngine environment.
  """
  if sys.modules.has_key('google.appengine.api.urlfetch'):
    return AppEngineUrlFetch()
  return UrlFetch()


class UrlFetch(object):
  """An API which provides a simple interface for performing HTTP requests.
  """

  def fetch(self, request):
    """TODO: Implement me."""
    assert False, "Not yet implemented"


class AppEngineUrlFetch(UrlFetch):
  """Implementation of UrlFetch using AppEngine's URLFetch API.
  """

  def fetch(self, request):
    """Performs a synchronous fetch request.
    
    Args:
      request: The http.Request object that contains the request information.
    
    Returns: An http.Response object.
    """
    method = request.get_method()
    url = request.get_url()
    body = request.post_body
    headers = { 'User-Agent': 'OpenSocial Python Client (AppEngine)' }
    result = urlfetch.fetch(
        method=method,
        url=url,
        payload=body,
        headers=headers)
    response = Response(result.status_code, result.content)
    return response


class Request(object):
  """This object is used to make a UrlFetch interface request.
  
  It also will sign a request with OAuth.
  """

  def __init__(self, url, method='GET', signed_params=None, post_body=None):
    self.post_body = post_body or ''
    self.oauth_request = oauth.OAuthRequest.from_request(method, url,
        parameters=signed_params)
    
  def sign_request(self, consumer, signature_method):
    """Add oauth parameters and sign the request with the given method.
    
    Args:
      consumer: The OAuthConsumer set with a key and secret.
      signature_method: A supported method for signing the built request.
    """
    params = {
      'oauth_consumer_key': consumer.key,
      'oauth_timestamp': oauth.generate_timestamp(),
      'oauth_nonce': oauth.generate_nonce(),
      'oauth_version': oauth.OAuthRequest.version,
    }
    self.set_parameters(params)
    self.oauth_request.sign_request(signature_method, consumer, None)
  
  def set_parameters(self, params):
    """Set the parameters for this request.
    
    Args:
      params: dict A dict of parameters.
    """
    for key, value in params.iteritems():
      self.oauth_request.set_parameter(key, value)
  
  def get_parameter(self, key):
    """Get the value of a particular parameter.
    
    Args:
      key: str The key of the requested parameter.
      
    Returns: The parameter value.
    """
    return self.oauth_request.get_parameter(keys)
  
  def get_method(self):
    """Returns the HTTP normalized method of this request.
    
    Returns: The normalized HTTP method.
    """
    return self.oauth_request.get_normalized_http_method()
  
  def get_url(self):
    """Get the full URL of this request, including the post body.
    
    Returns: The full URL for this request.
    """
    return self.oauth_request.to_url()
  
  def get_normalized_url(self):
    """Get the normalized URL for this request.
    
    Returns: The normalized URL for this request.
    """
    return self.oauth_request.get_normalized_http_url()

class Response(object):
  """Represents a response from the UrlFetch interface.
  """

  def __init__(self, status, content):
    self.status = status
    self.content = content
