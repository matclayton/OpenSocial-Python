import os
import logging
import wsgiref
import wsgiref.handlers

from opensocial.client import *
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Handler(webapp.RequestHandler):

  def get(self):
    self.test_friends('03067092798963641994')
 
  def get_container(self):
    config = ContainerConfig(oauth_consumer_key='orkut.com:623061448914',
        oauth_consumer_secret='uynAeXiWTisflWX99KU1D2q5',
        server_rest_base='http://sandbox.orkut.com/social/rest/')
        #server_rpc_base='http://sandbox.orkut.com/social/rpc')
    return ContainerContext(config)
    
  def test_friends(self, user_id):
    container = self.get_container()

    me = container.fetch_person(user_id)
    friends = container.fetch_friends(user_id)

    self.response.out.write('<h3>Test</h3>')
    self.output(me, friends)

  def test_batch(self, id, token):
    pass    

  def output(self, me, friends):
    self.response.out.write('%s\'s Friends: ' % me.get_display_name())
    if len(friends.items) == 0:
      self.response.out.write('You have no friends.')
    else:
      self.response.out.write('<ul>')
      for person in friends.items:
        self.response.out.write('<li>%s</li>' % person.get_display_name())
      self.response.out.write('</ul>')

def main():
  application = webapp.WSGIApplication([
      ('.*', Handler),
  ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
