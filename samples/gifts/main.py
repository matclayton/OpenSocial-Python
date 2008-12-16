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

import logging
import random
import wsgiref
import wsgiref.handlers

from opensocial import *
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

GIFTS = {
  'snakes': { 'name': 'some snakes', 'img': 'public/snakes.png' },
  'dictator': { 'name': 'a benevolent dictator', 'img': 'public/dictator.png' },
  'grail': { 'name': 'a holy grail', 'img': 'public/grail.png' },
}
USER_ID = '03067092798963641994'

class Gift(db.Model):

  name = db.StringProperty(required=True)
  sent_to = db.StringProperty(required=True)
  sent_from = db.StringProperty(required=True)
  sent_date = db.DateTimeProperty(auto_now=True)


class SocialData(object):
  
  def __init__(self):
    config = ContainerConfig(oauth_consumer_key='orkut.com:623061448914',
        oauth_consumer_secret='uynAeXiWTisflWX99KU1D2q5',
        server_rest_base='http://sandbox.orkut.com/social/rest/')
    self.container = ContainerContext(config)
    self.me = self.container.fetch_person(USER_ID)
    self.friends = self.container.fetch_friends(USER_ID)
  
  def get_friend(self, id):
    for friend in self.friends.items:
      if friend.get_id() == id:
        return friend
    return None


class GiftsHandler(webapp.RequestHandler):
  """The gifts application handler.
  
  TODO: Use Django templates instead of HTML strings.
  """
  
  def get(self):
    social_data = SocialData()
    
    query = Gift.all()
    query.order('-sent_date')
    gifts = query.fetch(1000)

    html = """
<html>
  <head>
    <title>OpenSocial - RESTful Gifts</title>
    <link rel="stylesheet" type="text/css" href="public/style.css">
  </head>
  <body>
"""

    self.output(html)
    self.output("""
Hello, <b>%s</b>, this application allows you to send and receives gifts with your
friends. Enjoy!<br/><br/>
""" % social_data.me.get_display_name())

    self.output('<form method="POST" action="/index.html">')
    self.output('Send <select name="gift">')
    for key, gift in GIFTS.iteritems():
      self.output('<option value="%s">%s</option>' % (key, gift.get('name')))
    self.output('<option value="random">a random gift</option>')
    self.output('</select> to <select name="to">')
    for friend in social_data.friends.items:
      self.output('<option value="%s">%s</option>' %
                  (friend.get_id(), friend.get_display_name()))
    self.output('</select> <input type="submit" value="Send It!"/></form>')

    num_gifts_received = 0
    num_gifts_sent = 0
    for gift in gifts:
      if gift.sent_to == social_data.me.get_id():
        num_gifts_received += 1
      if gift.sent_from == social_data.me.get_id():
        num_gifts_sent += 1

    self.output("""
<table class="layout"><tr><td>
<table class="list">
<tr><td colspan="3" class="header">Gifts Sent</td></tr>
""")
    if num_gifts_sent > 0:
      self.output("""
<tr class="sub-header"><td>Date</td><td>To</td><td>Gift</td></tr>
""")
      for gift in gifts:
        if gift.sent_from == social_data.me.get_id():
          gift_data = GIFTS.get(gift.name)
          friend = social_data.get_friend(gift.sent_to)
          if gift and friend:
            self.output('<tr>')
            self.output('<td>%s</td>' % gift.sent_date.strftime('%m-%d-%Y'))
            self.output('<td><img src="%s" class="thumbnail"><br/>%s</td>' %
                        (friend.get_field('thumbnailUrl'),
                         friend.get_display_name()))
            self.output('<td><img src="%s" class="gift"/><br/>%s</td>' %
                        (gift_data.get('img'), gift_data.get('name')))
            self.output('</tr>')
    else:
      self.output("""
<tr><td colspan="3">You have not sent any gifts... why not? </td></tr>
""")

    self.output("""
</table>
</td><td>
<table class="list">
<tr><td colspan="3" class="header">Gifts Received</td></tr>
""")
    
    if num_gifts_received > 0:
      self.output("""
<tr class="sub-header"><td>Date</td><td>From</td><td>Gift</td></tr>
""")
      for gift in gifts:
        if gift.sent_to == social_data.me.get_id():
          gift_data = GIFTS.get(gift.name)
          friend = social_data.get_friend(gift.sent_from)
          if gift and friend:
            self.output('<tr>')
            self.output('<td>%s</td>' % gift.sent_date.strftime('%m-%d-%Y'))
            self.output('<td><img src="%s" class="thumbnail"><br/>%s</td>' %
                        (friend.get_field('thumbnailUrl'),
                         friend.get_display_name()))
            self.output('<td><img src="%s" class="gift"/><br/>%s</td>' %
                        (gift_data.get('img'), gift_data.get('name')))
            self.output('</tr>')
    else:
      self.output("""
<tr><td colspan="3">You have not received any gifts. :-( </td></tr>
""")

    html = """
</table>
    </td></tr></table>
  </body>
</html>
"""
    self.output(html)
    
  def post(self):
    random.seed()
    social_data = SocialData()
    
    gift = self.request.get('gift')
    if gift == 'random':
      gift = GIFTS.keys()[random.randint(0, len(GIFTS) - 1)]
    to = self.request.get('to')
    sent_to = None
    friend = social_data.get_friend(to)
    if friend and GIFTS.has_key(gift):
      new_gift = Gift(name=gift,
                      sent_to=friend.get_id(),
                      sent_from=social_data.me.get_id())
      new_gift.put()
    self.redirect('/')
    
  def output(self, html):
    self.response.out.write(html)


def main():
  application = webapp.WSGIApplication([
      ('.*', GiftsHandler),
  ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
