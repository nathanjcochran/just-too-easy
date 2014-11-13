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

class Game(ndb.Model):
    length = ndb.IntegerProperty(default=6)
    status = msgprop.EnumProperty(GameStatus, required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)

    # Players: (current positions)
    red_o = ndb.KeyProperty(kind='Player', required=True)
    red_d = ndb.KeyProperty(kind='Player', required=True)
    blue_o = ndb.KeyProperty(kind='Player', required=True)
    blue_d = ndb.KeyProperty(kind='Player', required=True)

    # Scores:
    red_shots = ndb.KeyProperty(kind='Shot', repeated=True)
    blue_shots = ndb.KeyProperty(kind='Shot', repeated=True)

    def register_shot(self, player_key):
        """
        Register a shot for the player with the specified key
        
        Raises an Exception if the key is invalid or the game
        is over
        """

        # Get the actor who made the shot:
        side, position = self.side_and_position(player_key)

        if not side or not position:
            raise Exception("Error: invalid player")

        # Create the shot record:
        shot = Shot(parent = self.key)
        shot.player = player_key
        shot.position = position
        shot.side = side

        # If red scored:
        if side == Side.red:
            shot.against = self.blue_d
            shot.put()
            self.red_shots.append(shot.key)

            if len(self.red_shots) == self.length/2:
                temp = self.red_o
                self.red_o = self.red_d
                self.red_d = temp

            # Mark game complete if over:
            if len(self.red_shots) >= self.length:
                self.status = GameStatus.complete

        # If blue scored:
        elif side == Side.blue:
            shot.against = self.red_d
            shot.put()
            self.blue_shots.append(shot.key)

            if len(self.blue_shots) == self.length/2:
                temp = self.blue_o
                self.blue_o = self.blue_d
                self.blue_d = temp

            # Mark game complete if over:
            if len(self.blue_shots) >= self.length:
                self.status = GameStatus.complete

        self.put()

    def side_and_position(self, player_key):
        """
        Get the side and position of the specified player

        """
        if(player_key == self.red_o):
            return Side.red, Position.offense
        if(player_key == self.red_d):
            return Side.red, Position.defense
        if(player_key == self.blue_o):
            return Side.blue, Position.offense
        if(player_key == self.blue_d):
            return Side.blue, Position.defense

    def isComplete(self):
        return self.status == GameStatus.complete

    def red_score(self):
        return len(self.red_shots)

    def red_score_percentage(self):
        return len(self.red_shots) / float(self.length) * 100.0

    def blue_score(self):
        return len(self.blue_shots)

    def blue_score_percentage(self):
        return len(self.blue_shots) / float(self.length) * 100.0


class Shot(ndb.Model): # ancestor = Game => strongly consistent results
    player = ndb.KeyProperty(kind='Player', required=True)
    position = msgprop.EnumProperty(Position, required=True)
    side = msgprop.EnumProperty(Side, required=True)
    against = ndb.KeyProperty(kind='Player', required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)
