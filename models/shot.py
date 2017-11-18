from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

class Position(messages.Enum):
    offense = 1
    defense = 2
    either = 3

class Side(messages.Enum):
    red = 1
    blue = 2

class Image(ndb.Model):
    data = ndb.BlobProperty(required=True)

class Shot(ndb.Model): # ancestor = Game => strongly consistent results
    player = ndb.KeyProperty(kind='Player', required=True)
    position = msgprop.EnumProperty(Position, required=True)
    side = msgprop.EnumProperty(Side, required=True)
    against = ndb.KeyProperty(kind='Player', required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)
