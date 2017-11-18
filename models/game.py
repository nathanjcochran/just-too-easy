from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from random import shuffle
import elo

class GameStatus(messages.Enum):
    active = 1
    complete = 2
    deleted = 3

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

    # TrueSkill
    quality = ndb.IntegerProperty(required=True)

    def initialize(self, length, red_o, red_d, blue_o, blue_d):
        self.length = length
        self.status = GameStatus.active

        self.red_o = red_o
        self.red_d = red_d
        self.blue_o = blue_o
        self.blue_d = blue_d

        red_o = self.red_o.get()
        red_d = self.red_d.get()
        blue_o = self.blue_o.get()
        blue_d = self.blue_d.get()

        self.red_elo = (red_o.elo + red_d.elo) / 2
        self.blue_elo = (blue_o.elo + blue_d.elo) / 2

        self.quality = skill.calculate_quality((red_o, red_d), (blue_o, blue_d))

    def initialize_random(self, length, players):
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

        self.quality = skill.calculate_quality((red_o, red_d), (blue_o, blue_d))

    def initialize_matched(self, length, players):
        self.length = length
        self.status = GameStatus.active

        shuffle(players)
        p1 = players[0].get()
        p2 = players[1].get()
        p3 = players[2].get()
        p4 = players[3].get()

        red = (p1, p2)
        blue = (p3, p4)

        teams = {'red': red, 'blue': blue}
        quality = skill.calculate_quality(red, blue)

        r = (p1, p3)
        b = (p2, p4)
        q = skill.calculate_quality(r, b)
        if q > quality:
            teams = {'red': r, 'blue': b}
            quality = q

        r = (p1, p4)
        b = (p2, p3)
        q = skill.calculate_quality(r, b)
        if q > quality:
            teams = {'red': r, 'blue': b}
            quality = q

        red_o = teams['red'][0]
        red_d = teams['red'][1]
        blue_o = teams['blue'][0]
        blue_d = teams['blue'][1]

        self.red_o = red_o.key
        self.red_d = red_d.key
        self.blue_o = blue_o.key
        self.blue_d = blue_d.key

        self.red_elo = (red_o.elo + red_d.elo) / 2
        self.blue_elo = (blue_o.elo + blue_d.elo) / 2

        self.quality = quality

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

        # Adjust player's ratings if over:
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

        self.red_elo = (red_o.elo + red_d.elo) / 2
        self.blue_elo = (blue_o.elo + blue_d.elo) / 2

        if winning_side == Side.red:
            red_o.total_wins += 1
            red_d.total_wins += 1

            self.update_elo(red_o, red_d, self.red_elo, blue_o, blue_d, self.blue_elo)
            self.update_trueskill((red_o, red_d), (blue_o, blue_d))

        elif winning_side == Side.blue:
            blue_o.total_wins += 1
            blue_d.total_wins += 1

            self.update_elo(blue_o, blue_d, self.blue_elo, red_o, red_d, self.red_elo)
            self.update_trueskill((blue_o, blue_d), (red_o, red_d))

        else:
            raise Exception("Error: invalid winning side")

    def update_elo(self, winner1, winner2, winner_elo, loser1, loser2, loser_elo):
        winner_points, loser_points = elo.calculate(winner_elo, loser_elo)

        winner1.elo = winner1.elo + winner_points
        winner2.elo = winner2.elo + winner_points

        loser1.elo = loser1.elo + loser_points
        loser2.elo = loser2.elo + loser_points

    def update_trueskill(self, winners, losers):
        winner_updates, loser_updates = skill.update_ratings(winners, losers)

        for i in range(len(winners)):
            winners[i].mu = winner_updates[i].mu
            winners[i].sigma = winner_updates[i].sigma

        for i in range(len(losers)):
            losers[i].mu = loser_updates[i].mu
            losers[i].sigma = loser_updates[i].sigma


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

