from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

class GameStatus(messages.Enum):
    active = 1
    complete = 2
    deleted = 3

class Position(messages.Enum):
    offense = 1
    defense = 2
    either = 3

class Side(messages.Enum):
    red = 1
    blue = 2

class Image(ndb.Model):
    data = ndb.BlobProperty(required=True)

class Player(ndb.Model):
    name = ndb.StringProperty(required=True)
    image = ndb.KeyProperty(kind='Image')

class Actor(ndb.Model):
    player = ndb.KeyProperty(kind='Player', required=True)
    side = msgprop.EnumProperty(Side, required=True)
    position = msgprop.EnumProperty(Position, required=True)

class Game(ndb.Model):
    length = ndb.IntegerProperty(default=6)
    status = msgprop.EnumProperty(GameStatus, required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)

    # Players: (current positions)
    actors = ndb.StructuredProperty(Actor, repeated=True)

    # Scores:
    red_shots = ndb.KeyProperty(kind='Shot', repeated=True)
    blue_shots = ndb.KeyProperty(kind='Shot', repeated=True)

    def player(self, side, position):
        actor = next(a for a in self.actors if (a.side == side and a.position == position))
        return actor.player

class Shot(ndb.Model): # ancestor = Game => strongly consistent results
    player = ndb.KeyProperty(kind='Player', required=True)
    position = msgprop.EnumProperty(Position, required=True)
    side = msgprop.EnumProperty(Side, required=True)
    against = ndb.KeyProperty(kind='Player', required=True)
    shot_type = ndb.KeyProperty(kind='ShotType')
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)

class ShotType(ndb.Model):
    name = ndb.StringProperty(required=True)
    position = msgprop.EnumProperty(Position)


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
