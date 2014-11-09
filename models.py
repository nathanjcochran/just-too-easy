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

class Side(message.Enum):
    red = 1
    blue = 2

class Image(ndb.Model):
    data = ndb.BlobProperty()

class Player(ndb.Model):
    name = ndb.StringProperty()
    image = ndb.KeyProperty(kind='Image')

class Actor(ndb.Model):
    player = ndb.KeyProperty(kind='Player')
    side = msgprop.EnumProperty(Side, required=True)
    position = msgprop.EnumProperty(Position, required=True)

class Game(ndb.Model):
    length = ndb.IntegerProperty(default=6)
    status = msgprop.EnumProperty(GameStatus, required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

    # Players: (current positions)
    actors = nsb.StructuredProperty(kind='Actor', repeated=True)

    # Scores:
    red_shots = ndb.KeyProperty(kind='Shot', repeated=True)
    blue_shots = ndb.KeyProperty(kind='Shot', repeated=True)

    def player(side, position):
        actor = next(p for p in players if player.side == side and player.position == position)
        player = actor.player

class Shot(ndb.Model): # ancestor = Game => strongly consistent results
    player = ndb.KeyProperty(kind='Player')
    position = msgprop.EnumProperty(kind='Position')
    side = msgprop.EnumProperty(kind='Side')
    against = ndb.KeyProperty(kind='Player')
    shot_type = ndb.KeyProperty(kind='ShotType')
    timestamp = ndb.DateTimeProperty(auto_add_now=True)

class ShotType(ndb.Model):
    name = ndb.StringProperty()
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
