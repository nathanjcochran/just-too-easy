from protorpc import messages
from google.appengine.ext import ndb

class Player(ndb.Model):
    name = ndb.StringProperty()

class Game(ndb.Model):
    length = ndb.IntegerProperty()

    red_shots = ndb.KeyProperty(kind='Shot', repeated=True)
    red_offense = ndb.KeyProperty(kind='Player')
    red_defense = ndb.KeyProperty(kind='Player')

    blue_shots = ndb.KeyProperty(kind='Shot', repeated=True)
    blue_offense = ndb.KeyProperty(kind='Player')
    blue_defense = ndb.KeyProperty(kind='Player')

class Shot(ndb.Model):
    game = ndb.KeyProperty()
    player = ndb.KeyProperty()
#    position = ??
    shot_type = ndb.StringProperty()

class ShotType(ndb.Model):
    shot_type = ndb.StringProperty()
