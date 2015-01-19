from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from random import shuffle
import elo

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
    elo = ndb.IntegerProperty(required=True, default=1600)
    total_games = ndb.IntegerProperty(required=True, default=0)
    total_wins = ndb.IntegerProperty(required=True, default=0)
    image = ndb.KeyProperty(kind='Image')
    deleted = ndb.BooleanProperty(required=True, default=False)

    def win_percentage(self):
        if self.total_games > 0:
            return round(float(self.total_wins) / self.total_games * 100, 2)
        else:
            return None

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

    # Team Elo Ratings (at start of match):
    red_elo = ndb.IntegerProperty(required=True)
    blue_elo = ndb.IntegerProperty(required=True)

    def initialize(self, players, length):
        ndb.Model.__init__(self)
        self.length = length
        self.status = GameStatus.active

        shuffle(players)
        self.red_o = players[0]
        self.red_d = players[1]
        self.blue_o = players[2]
        self.blue_d = players[3]

        red_o = self.red_o.get()
        red_d = self.red_d.get()
        blue_o = self.blue_o.get()
        blue_d = self.blue_d.get()

        self.red_elo = (red_o.elo + red_d.elo) / 2
        self.blue_elo = (blue_o.elo + blue_d.elo) / 2

    def register_shot(self, player_key):
        """
        Register a shot for the player with the specified key
        
        Raises an Exception if the key is invalid or the game
        is over
        """

        # Get the side and position of the player who made the shot:
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

            # Red half time:
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

            # Blue half time:
            if len(self.blue_shots) == self.length/2:
                temp = self.blue_o
                self.blue_o = self.blue_d
                self.blue_d = temp

            # Mark game complete if over:
            if len(self.blue_shots) >= self.length:
                self.status = GameStatus.complete

        # Adjust player's elo ratings if over:
        if self.is_complete():
            red_o = self.red_o.get()
            red_d = self.red_d.get()
            blue_o = self.blue_o.get()
            blue_d = self.blue_d.get()

            self.adjust_player_ratings(red_o, red_d, blue_o, blue_d)

            red_o.put()
            red_d.put()
            blue_o.put()
            blue_d.put()

        self.put()

    def adjust_player_ratings(self, red_o, red_d, blue_o, blue_d):
        winning_side = self.winning_side()
        if winning_side == None:
            return

        red_o.total_games += 1
        red_d.total_games += 1
        blue_o.total_games += 1
        blue_d.total_games += 1

        if winning_side == Side.red:
            red_o.total_wins += 1
            red_d.total_wins += 1

            winner_points, loser_points = elo.calculate(self.red_elo, self.blue_elo)
            red_o.elo = red_o.elo + winner_points
            red_d.elo = red_d.elo + winner_points
            blue_o.elo = blue_o.elo + loser_points
            blue_d.elo = blue_d.elo + loser_points

        elif winning_side == Side.blue:
            blue_o.total_wins += 1
            blue_d.total_wins += 1

            winner_points, loser_points = elo.calculate(self.blue_elo, self.red_elo)
            blue_o.elo = blue_o.elo + winner_points
            blue_d.elo = blue_d.elo + winner_points
            red_o.elo = red_o.elo + loser_points
            red_d.elo = red_d.elo + loser_points

        else:
            raise Exception("Error: invalid winning side")

    def side_and_position(self, player_key):
        """
        Get the side and position of the specified player

        """
        if player_key == self.red_o:
            return Side.red, Position.offense
        if player_key == self.red_d:
            return Side.red, Position.defense
        if player_key == self.blue_o:
            return Side.blue, Position.offense
        if player_key == self.blue_d:
            return Side.blue, Position.defense

    def is_complete(self):
        return self.status == GameStatus.complete

    def winning_side(self):
        if not self.is_complete():
            return None
        elif len(self.red_shots) == self.length:
            return Side.red
        else:
            return Side.blue

    def red_score(self):
        return len(self.red_shots)

    def blue_score(self):
        return len(self.blue_shots)

    def red_elo_points_to_gain(self):
        return elo.calculate(self.red_elo, self.blue_elo)[0]

    def blue_elo_points_to_gain(self):
        return elo.calculate(self.blue_elo, self.red_elo)[0]

class Shot(ndb.Model): # ancestor = Game => strongly consistent results
    player = ndb.KeyProperty(kind='Player', required=True)
    position = msgprop.EnumProperty(Position, required=True)
    side = msgprop.EnumProperty(Side, required=True)
    against = ndb.KeyProperty(kind='Player', required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)
