import http
import logging
import urllib

from data import *
from errors import *
from opensocial import oauth
from opensocial import simplejson


class RestRequest(object):
  """Represents a pending REST request.
  """

  def __init__(self, path, fields=None):
    self.path = path
    self.fields = fields

  def make_http_request(self, config):
    """Generates a http.Request object for the UrlFetch interface.
    
    Args:
      config: The container config which contains the base REST URL.
    
    Returns: The http.Request object.
    """
    url = http.Url(config.server_rest_base + self.path)
    return http.Request(url, method='GET')


class RpcRequest(object):
  """Represents a pending RPC request.
  """

  def __init__(self, method, params):
    self.params = {
      'method': method,
      'params': params,
    }
  
  def make_http_request(self, config):
    """Generates a http.Request object for the UrlFetch interface.
    
    Args:
      config: The container config which contains the base RPC URL.
    
    Returns: The http.Request object.
    """
    url = http.Url(config.server_rpc_base)
    json_body = simplejson.dumps(self.params)
    return http.Request(url, method='POST', post_body=json_body)


class ContainerConfig(object):
  """Setup parameters for connecting to a container.
  """
  
  def __init__(self, oauth_consumer_key=None, oauth_consumer_secret=None,
               server_rpc_base=None, server_rest_base=None):
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
    self.config = config
    self.url_fetch = url_fetch or http.get_default_urlfetch()
    
  def supports_rpc(self):
    """Tells whether or not the container was setup for RPC protocol.
    
    Returns: bool Is this container using the RPC protocol?
    """
    return self.config.server_rpc_base is not None
  
  def fetch_person(self, user_id='@me'):
    """Fetches a person by user id.
    
    Args:
      user_id: str The person's container-specific id.
      
    Returns: A Person object representing the specified user id.
    """
    result = self._fetch_people(user_id, '@self')
    return Person.parse_json(result)

  def fetch_friends(self, user_id='@me'):
    """Fetches the friends of a given user by id.
    
    Args:
      user_id: str The person's container-specific id for which to retrieve
      friends.
      
    Returns: A Collection of Person objects.
    """
    result = self._fetch_people(user_id, '@friends')
    return Collection.parse_json(result, Person)
  
  def fetch_person_app_data(self, user_id, app_id='@app'):
    """Fetches app data for a specified person and app.
    
    Args:
      user_id: str The person's container-specific id.
      app_id (optional): str The application id.
      
    Returns: A dict populated with app data.
    """
    request = self.new_fetch_person_app_data(user_id, '@self', app_id)
    return self._execute_request(user_id, request)

  def fetch_friend_app_data(self, user_id, app_id='@app'):
    """Fetches app data for a group of friends and app.
    
    Args:
      user_id: str The person's container-specific id.
      app_id (optional): str The application id.
      
    Returns: A dict populated with app data.
    """
    request = self.new_fetch_person_app_data(user_id, '@friends', app_id)
    return self._execute_request(user_id, request)

  def _fetch_people(self, user_id, group_id):
    request = self.new_fetch_person_request(user_id, group_id)
    return self._execute_request(user_id, request)

  def new_fetch_person_request(self, user_id, group_id='@self'):
    if self.supports_rpc():
      return self._create_rpc_request('people.get',
                                      params={'userId': user_id,
                                              'groupId': group_id})
    return self._create_rest_request(('people', user_id, group_id))

  def new_fetch_person_app_data(self, user_id, group_id='@self', app_id='@app'):
    if self.supports_rpc():
      return self._create_rpc_request('appdata.get',
                                      params={'userId': user_id,
                                              'groupId': group_id,
                                              'appId': app_id})
    return self._create_rest_request(('appdata', user_id, group_id, app_id))  

  def _create_rest_request(self, components, fields=None):
    """TODO(davidbyttow): Handle fields."""
    return RestRequest('/'.join(components))

  def _create_rpc_request(self, service, params=None, **kwds):
    args = params or {}
    args.update(**kwds)
    return RpcRequest(service, args)

  def _execute_request(self, user_id, request):
    http_request = request.make_http_request(self.config)
    self._sign_request(user_id, http_request)
    http_response = self.url_fetch.fetch(http_request)
    return self._handle_response(http_response)
    
  def _handle_response(self, http_response):
    if http_response.status == 200:
      json = simplejson.loads(http_response.content)
      if 'code' in json:
        code = json.get('code')
        if code == 401:
          raise UnauthorizedRequest()
      return json
    else:
      raise BadRequest()

  def _sign_request(self, user_id, http_request):
    if (self.config.oauth_consumer_key is None or
        self.config.oauth_consumer_secret is None):
      return
    
    method = http_request.method
    url = http_request.url.base
    post_body = http_request.post_body
    params = { 'xoauth_requestor_id': user_id }
    if post_body:
      params[post_body] = ''
    
    consumer = oauth.OAuthConsumer(self.config.oauth_consumer_key,
                                   self.config.oauth_consumer_secret)
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer,
        http_method=method,
        http_url=url,
        parameters=params)
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
    oauth_request.sign_request(signature_method, consumer, None)

    if post_body:
      http_request.url = http.Url(oauth_request.get_normalized_http_url())
      http_request.post_body = oauth_request.to_postdata()
    else:
      http_request.url = http.Url(oauth_request.to_url())
      http_request.post_body = None
    return http_request


class RequestBatch(object):
  """This class will manage the batching of requests.
  """
  
  def __init__(self, user_context, client_context):
    self.user = user_context
    self.client = client_context
    self.requests = {}
  
  def add(self, key, request):
    self.requests[key] = request
