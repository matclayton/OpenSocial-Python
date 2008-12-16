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
