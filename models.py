from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

class Image(ndb.Model):
    data = ndb.BlobProperty()

class Player(ndb.Model):
    name = ndb.StringProperty()
    image = ndb.KeyProperty(kind="Image")

class GameStatus(messages.Enum):
    active = 1
    complete = 2
    deleted = 3

class Game(ndb.Model):
    length = ndb.IntegerProperty()
    status = msgprop.EnumProperty(GameStatus, required=True)

    red_shots = ndb.KeyProperty(kind='Shot', repeated=True)
    blue_shots = ndb.KeyProperty(kind='Shot', repeated=True)

    red_offense = ndb.KeyProperty(kind='Player')
    red_defense = ndb.KeyProperty(kind='Player')

    blue_offense = ndb.KeyProperty(kind='Player')
    blue_defense = ndb.KeyProperty(kind='Player')

class Shot(ndb.Model): # ancestor = Game => strongly consistent results
    game = ndb.KeyProperty(kind="Game")
    player = ndb.KeyProperty(kind="Player")
    against = ndb.KeyProperty(kind="Player")
    shot_type = ndb.StringProperty()

class ShotType(ndb.Model):
    name = ndb.StringProperty()
#    position = ??




#
# How many games has X won?
#
# How many games has X won with Y on his/her team?
#
# How many games has X won against Y?
#
# How many shots has X made against Y?
# 
# Who has made the most shots of type X?
#
#
#
#
