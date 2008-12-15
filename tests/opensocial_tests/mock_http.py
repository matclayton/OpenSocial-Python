import logging
import urllib
from opensocial.client import http


class ResponseRecord(object):
  
  def __init__(self, request, response):
    self.request = request
    self.response = response


class MockUrlFetch(http.UrlFetch):
  
  def __init__(self):
    self.records = []
    self.default_response = http.Response(500, '')

  def add_response(self, request, response):
    self.records.append(ResponseRecord(request, response))

  def _lookup_request(self, request):
    for record in self.records:
      url = request.url.build_full_url()
      other_url = record.request.url.build_full_url()
      if (record.request.method == request.method and
          url == other_url and
          record.request.post_body == request.post_body):
        return record.response
    return self.default_response
  
  def fetch(self, request):
    response = self._lookup_request(request)
    return response
