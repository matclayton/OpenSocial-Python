from client import data
from client import simplejson


VIEWER_FIELDS = {
  'id': '101',
  'name': {'givenName': 'Kenny', 'familyName': ''},
}

FRIEND_COLLECTION_FIELDS = [
  { 
    'id': '102',
    'name': {'givenName': 'Stan', 'familyName': 'Marsh'},
  },
  { 
    'id': '103',
    'name': {'givenName': 'Kyle', 'familyName': 'Broflovski'},
  },
  { 
    'id': '104',
    'name': {'givenName': 'Eric', 'familyName': 'Cartman'},
  },
]

VIEWER = data.Person(VIEWER_FIELDS)

FRIENDS = []
for friend_fields in FRIEND_COLLECTION_FIELDS:
  FRIENDS.append(data.Person(friend_fields))

FRIEND_COLLECTION = data.Collection(FRIENDS, 0, len(FRIENDS))

NO_AUTH = { 'code': 401 }
