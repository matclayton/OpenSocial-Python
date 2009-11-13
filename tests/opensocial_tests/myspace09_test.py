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

__author__ = 'smadyalamajalu@myspace-inc.com (Sushruth Madyalamajalu)'


import unittest

import opensocial


class TestMySpace09(unittest.TestCase):
  
  def setUp(self):
    self.config = opensocial.ContainerConfig(
        oauth_consumer_key='http://www.myspace.com/503369944',
        oauth_consumer_secret='a99b44c5e6bf4f82ad3b0963513f0d0b682afe517cbd4c51a40d7a5b06472966',
        server_rest_base='http://opensocial.myspace.com/roa/09')
    self.container = opensocial.ContainerContext(self.config)
    self.user_id = '384066058'

  def validate_user(self, user):
    self.assertEquals("myspace.com.person." + self.user_id,  user.get_id())

  def validate_friends(self, friends):
    self.assertEquals(3, len(friends))
    self.assertEquals(3, int(friends.totalResults) )
    self.assertEquals('myspace.com.person.6221', friends[0].get_id())
    self.assertEquals('myspace.com.person.360215256', friends[1].get_id())
    
  def do_fetch_person(self, use_rpc, fields=None):
    self.container.set_allow_rpc(use_rpc)
    person = self.container.fetch_person(self.user_id, fields)
    return person

  def do_fetch_friends(self, use_rpc, fields=None):
    self.container.set_allow_rpc(use_rpc)
    friends = self.container.fetch_friends(self.user_id, fields)
    return friends

  def test_fetch_person_rest(self):
    person = self.do_fetch_person(False)
    self.validate_user(person)
    
  def test_fetch_friends_rest(self):
    friends = self.do_fetch_friends(False)
    self.validate_friends(friends)
    
  def test_fetch_person_fields_rest(self):
    person = self.do_fetch_person(False, ['displayName'])
    self.assertEquals('SushTest', person.get_field('displayName'))

  def test_fetch_supportedfields_rest(self):
    self.container.set_allow_rpc(False)
    personfields= self.container.fetch_supportedfields( self.user_id, 'people')
    self.assertNotEquals( personfields.index("name") , -1  )
    groupsfields = self.container.fetch_supportedfields( self.user_id, 'groups')
    self.assertNotEquals( groupsfields.index("title") , -1  )
    albumsfields = self.container.fetch_supportedfields( self.user_id, 'albums')
    self.assertNotEquals( albumsfields.index("mediaType") , -1  )

  def test_fetch_group_rest(self):
    self.container.set_allow_rpc(False)
    groups = self.container.fetch_groups(self.user_id)
    self.assertEquals(int(groups.totalResults), 2)
    self.assertEquals(groups[0].get_title(), "FriendCategory1")
    groups = self.container.fetch_groups(self.user_id, {'startIndex': 2, 'count': 1})
    self.assertEquals(groups[0].get_title(), "FriendCategory2")

  def test_fetch_album_rest(self):
    self.container.set_allow_rpc(False)
    albums = self.container.fetch_albums(self.user_id)
    self.assertTrue(int(albums.totalResults) > 8)
    albums = self.container.fetch_albums(self.user_id,'myspace.com.album.1407969')
    self.assertEquals(albums['caption'], "allBUMs")

  def test_fetch_mediaitem_rest(self):
    self.container.set_allow_rpc(False)
    mediaitems = self.container.fetch_mediaitems(self.user_id,'myspace.com.album.1417886')
    self.assertEquals(int(mediaitems.totalResults), 3)
    mediaitems = self.container.fetch_mediaitems(self.user_id,'myspace.com.album.1417886', 'myspace.com.mediaItem.image.23434774')
    self.assertEquals( mediaitems['title'], "doink" )
        
  def test_fetch_post_notification(self):
    self.container.set_allow_rpc(False)
    recipients = ["384066058" , "360215256"]
    mediaitems = ["http://opensocial.myspace.com/roa/09/mediaItems/360215256/@self/myspace.com.album.1417886/myspace.com.mediaItem.image.23434774",
                  "http://opensocial.myspace.com/roa/09/mediaItems/360215256/@self/myspace.com.album.1417886/myspace.com.mediaItem.image.23434774"]
    tp =[]
    p1 ={}
    p2={}
    p1["key"] = "content"
    p1["value"]= "Hi ${recipient}, This is the a test message."
    p2["key"] = "somethingelse"
    p2["value"]= "okie"
    tp.append(p1);
    tp.append(p2);
    notification =  self.container.create_notification(self.user_id, recipients, mediaitems,tp)
    self.assertNotEqual( notification['statusLink'].find('http://') , -1 )
    notification =  self.container.create_notification("@me", recipients, mediaitems,tp , {'xoauth_requestor_id':360215256})
    self.assertNotEqual( notification['statusLink'].find('http://') , -1 )

  def test_fetch_status_mood_and_Comments(self):
    statusmood  = self.container.fetch_statusmood(self.user_id)
    statusmoodcomments  = self.container.fetch_statusmoodcomments(self.user_id, {'postedDate': statusmood['moodStatusLastUpdated']})
    self.assertNotEqual( len(statusmoodcomments) , 0)

  def test_fetch_profileComments(self):
    profilecomment = self.container.fetch_profilecomments(self.user_id)
    self.assertNotEqual(len(profilecomment) , 0)

  def test_fetch_activity_request(self):
    activity = self.container.fetch_activity(self.user_id)
    self.assertNotEquals( len(activity) , 0 )
    activity = self.container.fetch_activity(self.user_id, '@self' ,'@app')

  def test_create_album_request(self):
    album = self.container.create_album(self.user_id, {'caption':'Test Album1'} )
    self.assertNotEqual( album['statusLink'].find('http://') , -1 )

  def test_batch(self):
    batch = opensocial.request.RequestBatch()
    batch.add_request('me',
                      opensocial.request.FetchPersonRequest(self.user_id))
    batch.add_request('friends',
                      opensocial.request.FetchPeopleRequest(self.user_id,
                                                            '@friends'))
    batch.send(self.container)
    me = batch.get('me')
    friends = batch.get('friends')
    self.validate_user(me)
    self.validate_friends(friends)

