#!/usr/bin/python2.4
#
# Copyright 2008 Google Inc. All Rights Reserved.

"""Errors used on the Python opensocial client libraries.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


class Error(Exception):
  """Base opensocial.client error type.
  """

class ConfigError(Error):
  """Raised when the client has not been configured properly.
  """
  

class BadResponse(Error):
  """Raised when the status code is not OK or data returned is invalid.
  """


class BadRequest(Error):
  """Raised when a malformed request is detected.
  """


class UnauthorizedRequest(Error):
  """Raised when a request failed due to bad authorization credentials.
  """
