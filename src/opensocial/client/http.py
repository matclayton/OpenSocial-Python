import logging
import os
import sys
import urllib
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
    data = None
    request_url = request.url.build_full_url()
    if request.post_body is not None:
      post_body = request.post_body
      result = urlfetch.fetch(url=request_url,
          payload=post_body,
          method=urlfetch.POST,
          headers={'Content-Type': 'application/x-www-form-urlencoded',
                   'User-Agent': 'OpenSocial API Client (AppEngine)',
                   'Content-Length': len(post_body)})
    else:
      result = urlfetch.fetch(request_url,
          method=urlfetch.GET,
          headers={'User-Agent': 'OpenSocial API Client (AppEngine)'})
    response = Response(result.status_code, result.content)
    return response


class Url(object):
  """URL class for wrapping a base URL string and a set of query parameters.
  """
  def __init__(self, base):
    self.base = base
    self.params = {}

  def add_query_param(self, key, value):
    """Add a key/value pair as a query parameter.
    
    Args:
      key: str
      value: str
    """
    self.params[key] = value
  
  def remove_query_param(self, key):
    """Remove a key/value pair from the query string.
    
    Args:
      key: str
    """
    try:
      del self.params[key]
    except:
      pass
    
  def build_full_url(self):
    """Builds the final URL string from the base and query parameters.
    
    Returns: The URL string.
    """
    url = self.base
    op = '?'
    for key, value in self.params.iteritems():
      url += '%s%s=%s' % (op, key, value)
      op = '&'
    return url

class Request(object):
  """This object is used to make a UrlFetch interface request.
  """

  def __init__(self, url, post_body=None, method='GET'):
    self.url = url
    self.method = method
    self.post_body = post_body
    

class Response(object):
  """Represents a response from the UrlFetch interface.
  """

  def __init__(self, status, content):
    self.status = status
    self.content = content
