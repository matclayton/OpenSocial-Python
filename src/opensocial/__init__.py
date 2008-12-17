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


import httplib
import urllib

import http

from data import *
from errors import *
from opensocial import oauth, simplejson
from request import *


class ContainerConfig(object):
  """Setup parameters for connecting to a container."""
  
  def __init__(self, oauth_consumer_key=None, oauth_consumer_secret=None,
               server_rpc_base=None, server_rest_base=None):
    """Constructor for ContainerConfig.
    
    If no oauth parameters are present, then oauth will not be used to sign
    requests, and as such, the client connection will most likely not work.
    
    At least one of server_rpc_base or server_rest_base should be specified,
    otherwise, all requests will fail. If both are supplied, the container
    will attempt to default to rpc and fall back on REST.

    """
    self.oauth_consumer_key = oauth_consumer_key 
    self.oauth_consumer_secret = oauth_consumer_secret
    self.server_rpc_base = server_rpc_base
    self.server_rest_base = server_rest_base


class ContainerContext(object):
  """The context for a container connection.
  
  This class manages the connection to a specific container and provides
  methods for fetching common data via either te REST or RPC protocol, depending
  on the configuration.

  """
  
  def __init__(self, config, url_fetch=None):
    """Constructor for ContainerContext.
    
    If a UrlFetch implementation is not given, will attempt to construct
    the default implementation based on the environment.
    
    Args:
      config: The ContainerConfig to use for this connection.
      url_fetch: (optional) An implementation of the UrlFetch interface.

    """
    self.config = config
    self.url_fetch = url_fetch or http.get_default_urlfetch()
    self.oauth_signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1() 
    self.oauth_consumer = None
    if self.config.oauth_consumer_key and self.config.oauth_consumer_secret:
      self.oauth_consumer = oauth.OAuthConsumer(
          self.config.oauth_consumer_key,
          self.config.oauth_consumer_secret)
    
  def supports_rpc(self):
    """Tells whether or not the container was setup for RPC protocol.
    
    Returns: bool Is this container using the RPC protocol?
    
    TODO: Figure out what is going wrong with POST body signing, fix and
    re-enable this.

    """
    return False
#    return self.config.server_rpc_base is not None
  
  def fetch_person(self, user_id='@me'):
    """Fetches a person by user id.
    
    Args:
      user_id: str The person's container-specific id.
      
    Returns: A Person object representing the specified user id.

    """
    request = FetchPersonRequest(user_id)
    return self.send_request(request)

  def fetch_friends(self, user_id='@me'):
    """Fetches the friends of a given user by id.
    
    Args:
      user_id: str The person's container-specific id for which to retrieve
      friends.
      
    Returns: A Collection of Person objects.

    """
    request = FetchPeopleRequest(user_id, '@friends')
    return self.send_request(request)


  def send_request(self, request, use_rest=False):
    """Sends the request.
    
    May throw a BadRequestError, BadResponseError or 
    UnauthorizedRequestError exceptions.

    Args:
      request: A Request object.
      use_rest: bool (optional) If True, will just use the REST protocol.
      
    Returns: The OpenSocial object returned from the container.

    """
    http_request = None
    if not use_rest and self.supports_rpc():
      http_request = request.make_rpc_request(self.config.server_rpc_base)
    else:
      http_request = request.make_rest_request(self.config.server_rest_base)

    # Attempt to sign this request.
    if self.oauth_consumer and self.oauth_signature_method:
      http_request.sign_request(self.oauth_consumer,
                                self.oauth_signature_method)
   
    http_response = self.url_fetch.fetch(http_request)
    json = self._handle_response(http_response)
    return request.process_json(json)
  
  def send_request_batch(self, batch, use_rest=False):
    """Send a batch of requests.
    
    Batches are only useful when RPC is supported. Otherwise, all requests
    are sent synchronously. May throw a BadRequest, BadResponse or
    UnauthorizedRequest exceptions.

    TODO: Put all requests together if RPC is supported.

    Args:
      batch: The RequestBatch object.
      use_rest: bool (optional) If True, will just use the REST protocol.

    """
    for key, request in batch.requests.iteritems():
      batch._set_data(key, self.send_request(request, use_rest))
      
  def _handle_response(self, http_response):
    """ If status code "OK", then we can safely inspect the returned JSON."""
    if http_response.status == httplib.OK:
      json = simplejson.loads(http_response.content)
      # Check for any JSON-RPC 2.0 errors.
      if 'code' in json:
        code = json.get('code')
        if code == httplib.UNAUTHORIZED:
          raise UnauthorizedRequestError(http_response)
        else:
          raise BadResponseError(http_response)
      return json
    else:
      raise BadRequestError(http_response)
