from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from random import shuffle
from datetime import datetime
from shot import *
import elo
import skill

class GameStatus(messages.Enum):
    active = 1
    complete = 2
    deleted = 3

class Game(ndb.Model):
    length = ndb.IntegerProperty(default=6)
    status = msgprop.EnumProperty(GameStatus, required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, required=True)
    end_timestamp = ndb.DateTimeProperty()
    stakes = ndb.DateTimeProperty(default=1)

    # Players: (current positions)
    red_o = ndb.KeyProperty(kind='Player', required=True)
    red_d = ndb.KeyProperty(kind='Player', required=True)
    blue_o = ndb.KeyProperty(kind='Player', required=True)
    blue_d = ndb.KeyProperty(kind='Player', required=True)

    # Shots:
    shots = ndb.StructuredProperty(Shot, repeated=True)
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
    
    def initialize_high_stakes(self, length,  red_o, red_d, blue_o, blue_d):
        self.stakes = 2
        self.initialize(length,  red_o, red_d, blue_o, blue_d)

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

        if self.status != GameStatus.active:
            raise Exception("Error: game not active")

        # Get the side and position of the player who made the shot:
        side, position = self.side_and_position(player_key)

        if not side or not position:
            raise Exception("Error: invalid player")

        # Create the shot record:
        shot = Shot(parent = self.key)
        shot.player = player_key
        shot.position = position
        shot.side = side
        shot.timestamp = datetime.now()

        # If red scored:
        if side == Side.red:
            shot.against = self.blue_d
            self.shots.append(shot)

            # Red half time:
            if self.red_score == self.length/2:
                temp = self.red_o
                self.red_o = self.red_d
                self.red_d = temp

            # Mark game complete if over:
            if self.red_score >= self.length:
                self.status = GameStatus.complete
                self.end_timestamp = shot.timestamp

        # If blue scored:
        elif side == Side.blue:
            shot.against = self.red_d
            self.shots.append(shot)

            # Blue half time:
            if self.blue_score == self.length/2:
                temp = self.blue_o
                self.blue_o = self.blue_d
                self.blue_d = temp

            # Mark game complete if over:
            if self.blue_score >= self.length:
                self.status = GameStatus.complete
                self.end_timestamp = shot.timestamp

        # Adjust player's ratings if over:
        if self.is_complete:
            red_o = self.red_o.get()
            red_d = self.red_d.get()
            blue_o = self.blue_o.get()
            blue_d = self.blue_d.get()

            self.adjust_player_statistics(red_o, red_d, blue_o, blue_d)

            red_o.put()
            red_d.put()
            blue_o.put()
            blue_d.put()

        self.put()

    def adjust_player_statistics(self, red_o, red_d, blue_o, blue_d):
        # TODO: Hack to turn shot keys into structured properties
        if len(self.shots) == 0:
            self.shots = ndb.get_multi(self.red_shots + self.blue_shots)
            self.shots.sort(key=lambda shot: shot.timestamp)
            self.end_timestamp = self.shots[-1].timestamp
            self.put()

        winning_side = self.winning_side
        if winning_side == None:
            return

        # Last played:
        red_o.last_played = self.timestamp
        red_d.last_played = self.timestamp
        blue_o.last_played = self.timestamp
        blue_d.last_played = self.timestamp

        # Games Played:
        red_o.total_games += 1
        red_d.total_games += 1
        blue_o.total_games += 1
        blue_d.total_games += 1

        # Positional Games Played/Halftimes Reached:
        if self.red_halftime_reached:
            # Flipped because of halftimes:
            red_o.red_d_halftimes += 1
            red_d.red_o_halftimes += 1

            red_o.red_d_games += 1
            red_d.red_o_games += 1
        else:
            red_o.red_o_games += 1
            red_d.red_d_games += 1

        if self.blue_halftime_reached:
            # Flipped because of halftimes:
            blue_o.blue_d_halftimes += 1
            blue_d.blue_o_halftimes += 1

            blue_o.blue_d_games += 1
            blue_d.blue_o_games += 1
        else:
            blue_o.blue_o_games += 1
            blue_d.blue_d_games += 1

        # Wins/elo/trueskill:
        self.red_elo = (red_o.elo + red_d.elo) / 2
        self.blue_elo = (blue_o.elo + blue_d.elo) / 2
        if winning_side == Side.red:
            # Flipped because of halftimes:
            red_o.red_d_wins += 1
            red_d.red_o_wins += 1

            self.update_elo(red_o, red_d, self.red_elo, blue_o, blue_d, self.blue_elo)
            self.update_trueskill((red_o, red_d), (blue_o, blue_d))

        elif winning_side == Side.blue:
            # Flipped because of halftimes:
            blue_o.blue_d_wins += 1
            blue_d.blue_o_wins += 1

            self.update_elo(blue_o, blue_d, self.blue_elo, red_o, red_d, self.red_elo)
            self.update_trueskill((blue_o, blue_d), (red_o, red_d))

        else:
            raise Exception("Error: invalid winning side")

        # Shots:
        for shot in self.shots:
            player = shot.player.get() # Should be cached
            if not player:
                raise Exception("Bad player key: " + shot.player.urlsafe())

            if shot.side == Side.red and shot.position == Position.offense:
                player.red_o_shots += 1
            elif shot.side == Side.red and shot.position == Position.defense:
                player.red_d_shots += 1
            elif shot.side == Side.blue and shot.position == Position.offense:
                player.blue_o_shots += 1
            elif shot.side == Side.blue and shot.position == Position.defense:
                player.blue_d_shots += 1
            else:
                raise Exception("Error: invalid side/position")
            
            startingSide, startingPosition = self.starting_side_and_position(shot.player)
            if startingSide == Side.red and startingPosition == Position.offense:
                player.red_o_start_shots += 1
            elif startingSide == Side.red and startingPosition == Position.defense:
                player.red_d_start_shots += 1
            elif startingSide == Side.blue and startingPosition == Position.offense:
                player.blue_o_start_shots += 1
            elif startingSide == Side.blue and startingPosition == Position.defense:
                player.blue_d_start_shots += 1
            else:
                raise Exception("Error: invalid starting position")
                
    def update_elo(self, winner1, winner2, winner_elo, loser1, loser2, loser_elo):
        winner_points, loser_points = elo.calculate(winner_elo, loser_elo)

        winner1.elo = winner1.elo + winner_points * self.stakes
        winner2.elo = winner2.elo + winner_points * self.stakes

        loser1.elo = loser1.elo + loser_points * self.stakes
        loser2.elo = loser2.elo + loser_points * self.stakes

    def update_trueskill(self, winners, losers):
        winner_updates, loser_updates = skill.update_ratings(winners, losers)

        for i in range(len(winners)):
            winners[i].mu = winners[i].mu + self.stakes * (winner_updates[i].mu - winners[i].mu)
            winners[i].sigma = winner_updates[i].sigma

        for i in range(len(losers)):
            losers[i].mu = losers[i].mu - self.stakes * (losers[i].mu - loser_updates[i].mu)
            losers[i].sigma = loser_updates[i].sigma

    def starting_side_and_position(self, player_key):
        if player_key == self.red_o:
            if self.red_halftime_reached:
                return Side.red, Position.defense
            else:
                return Side.red, Position.offense
        if player_key == self.red_d:
            if self.red_halftime_reached:
                return Side.red, Position.offense
            else:
                return Side.red, Position.defense
        if player_key == self.blue_o:
            if self.blue_halftime_reached:
                return Side.blue, Position.defense
            else:
                return Side.blue, Position.offense
        if player_key == self.blue_d:
            if self.blue_halftime_reached:
                return Side.blue, Position.offense
            else:
                return Side.blue, Position.defense

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

    @property
    def is_complete(self):
        return self.status == GameStatus.complete

    @property
    def red_score(self):
        return sum(shot.side == Side.red for shot in self.shots)

    @property
    def blue_score(self):
        return sum(shot.side == Side.blue for shot in self.shots)

    @property
    def red_halftime_reached(self):
        return self.red_score >= self.length/2

    @property
    def blue_halftime_reached(self):
        return self.blue_score >= self.length/2

    @property
    def winning_side(self):
        if not self.is_complete:
            return None
        elif self.red_score == self.length:
            return Side.red
        elif self.blue_score == self.length:
            return Side.blue

    @property
    def red_elo_points_to_gain(self):
        return elo.calculate(self.red_elo, self.blue_elo)[0]

    @property
    def blue_elo_points_to_gain(self):
        return elo.calculate(self.blue_elo, self.red_elo)[0]
