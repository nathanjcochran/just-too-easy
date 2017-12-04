from google.appengine.ext import ndb
from datetime import *
import skill
import elo

RANKED_THRESHOLD = 10 # Number of games you have to play to be ranked

class Image(ndb.Model):
    data = ndb.BlobProperty(required=True)

class Player(ndb.Model):
    # Basic Info:
    name = ndb.StringProperty(required=True)
    image = ndb.KeyProperty(kind='Image')
    deleted = ndb.BooleanProperty(required=True, default=False)
    last_played = ndb.DateTimeProperty(required=True, default=datetime.min)

    # Elo:
    elo = ndb.IntegerProperty(required=True, default=1600)

    # TrueSkill
    mu = ndb.FloatProperty(required=True, default=skill.DEFAULT_MU)
    sigma = ndb.FloatProperty(required=True, default=skill.DEFAULT_SIGMA)

    @property
    def trueskill_rating(self):
        return skill.get_rating(self)

    def trueskill_gain(self, teammate, opponents):
        ratings = skill.update_ratings((self, teammate), opponents)[0][0]
        rating = skill.calculate_rating(ratings.mu, ratings.sigma)

        return rating - self.trueskill_rating

    def trueskill_loss(self, teammate, opponents):
        ratings = skill.update_ratings(opponents, (self, teammate))[1][0]
        rating = skill.calculate_rating(ratings.mu, ratings.sigma)

        return self.trueskill_rating - rating

    # Games played:
    # NOTE: "o" and "d" refer to offense/defense *starting positions*
    red_o_games = ndb.IntegerProperty(required=True, default=0)
    red_d_games = ndb.IntegerProperty(required=True, default=0)
    blue_o_games = ndb.IntegerProperty(required=True, default=0)
    blue_d_games = ndb.IntegerProperty(required=True, default=0)

    # For sake of query indexes:
    total_games = ndb.IntegerProperty(required=True, default=0)

    @property
    def red_games(self):
        return self.red_o_games + self.red_d_games

    @property
    def blue_games(self):
        return self.blue_o_games + self.blue_d_games

    @property
    def offense_games(self):
        return self.red_o_games + self.blue_o_games

    @property
    def defense_games(self):
        return self.red_d_games + self.blue_d_games

    # Is Ranked:
    @property
    def is_ranked(self):
        return self.total_games >= RANKED_THRESHOLD

    # Halftimes reached:
    red_o_halftimes = ndb.IntegerProperty(required=True, default=0)
    red_d_halftimes = ndb.IntegerProperty(required=True, default=0)
    blue_o_halftimes = ndb.IntegerProperty(required=True, default=0)
    blue_d_halftimes = ndb.IntegerProperty(required=True, default=0)

    @property
    def red_halftimes(self):
        return self.red_o_halftimes + self.red_d_halftimes

    @property
    def blue_halftimes(self):
        return self.blue_o_halftimes + self.blue_d_halftimes

    @property
    def offense_halftimes(self):
        return self.red_o_halftimes + self.blue_o_halftimes

    @property
    def defense_halftimes(self):
        return self.red_d_halftimes + self.blue_d_halftimes

    @property
    def total_halftimes(self):
        return self.red_halftimes + self.blue_halftimes

    # Wins:
    red_o_wins = ndb.IntegerProperty(required=True, default=0)
    red_d_wins = ndb.IntegerProperty(required=True, default=0)
    blue_o_wins = ndb.IntegerProperty(required=True, default=0)
    blue_d_wins = ndb.IntegerProperty(required=True, default=0)

    @property
    def red_wins(self):
        return self.red_o_wins + self.red_d_wins

    @property
    def blue_wins(self):
        return self.blue_o_wins + self.blue_d_wins

    @property
    def offense_wins(self):
        return self.red_o_wins + self.blue_o_wins

    @property
    def defense_wins(self):
        return self.red_d_wins + self.blue_d_wins

    @property
    def total_wins(self):
        return self.red_wins + self.blue_wins

    # Shots:
    # NOTE: These are the total number of shots *from the given
    # offense/defense position*
    red_o_shots = ndb.IntegerProperty(required=True, default=0)
    red_d_shots = ndb.IntegerProperty(required=True, default=0)
    blue_o_shots = ndb.IntegerProperty(required=True, default=0)
    blue_d_shots = ndb.IntegerProperty(required=True, default=0)

    # NOTE: These are the total number of shots in games where
    # the player *started in the given offense/defense position*
    red_o_game_shots = ndb.IntegerProperty(required=True, default=0)
    red_d_game_shots = ndb.IntegerProperty(required=True, default=0)
    blue_o_game_shots = ndb.IntegerProperty(required=True, default=0)
    blue_d_game_shots = ndb.IntegerProperty(required=True, default=0)

    @property
    def red_shots(self):
        return self.red_o_game_shots + self.red_d_game_shots

    @property
    def blue_shots(self):
        return self.blue_o_game_shots + self.blue_d_game_shots

    @property
    def offense_shots(self):
        return self.red_o_game_shots + self.blue_o_game_shots

    @property
    def defense_shots(self):
        return self.red_d_game_shots + self.blue_d_game_shots

    @property
    def total_shots(self):
        return self.red_o_game_shots + self.red_d_game_shots + self.blue_o_game_shots + self.blue_d_game_shots

    # Win Rate:
    @property
    def red_o_win_percentage(self):
        if self.red_o_games > 0:
            return round(float(self.red_o_wins) / self.red_o_games * 100, 2)
        else:
            return None

    @property
    def red_d_win_percentage(self):
        if self.red_d_games > 0:
            return round(float(self.red_d_wins) / self.red_d_games * 100, 2)
        else:
            return None

    @property
    def blue_o_win_percentage(self):
        if self.blue_o_games > 0:
            return round(float(self.blue_o_wins) / self.blue_o_games * 100, 2)
        else:
            return None

    @property
    def blue_d_win_percentage(self):
        if self.blue_d_games > 0:
            return round(float(self.blue_d_wins) / self.blue_d_games * 100, 2)
        else:
            return None


    @property
    def red_win_percentage(self):
        if self.red_games > 0:
            return round(float(self.red_wins) / self.red_games * 100, 2)
        else:
            return None

    @property
    def blue_win_percentage(self):
        if self.blue_games > 0:
            return round(float(self.blue_wins) / self.blue_games * 100, 2)
        else:
            return None

    @property
    def offense_win_percentage(self):
        if self.offense_games > 0:
            return round(float(self.offense_wins) / self.offense_games * 100, 2)
        else:
            return None

    @property
    def defense_win_percentage(self):
        if self.defense_games > 0:
            return round(float(self.defense_wins) / self.defense_games * 100, 2)
        else:
            return None

    @property
    def win_percentage(self):
        if self.total_games > 0:
            return round(float(self.total_wins) / self.total_games * 100, 2)
        else:
            return None

    # Average Shots Per Game:
    @property
    def average_shots_per_red_o_game(self):
        return self.red_o_game_shots / self.red_o_games

    @property
    def average_shots_per_red_d_game(self):
        return self.red_d_game_shots / self.red_d_games

    @property
    def average_shots_per_blue_o_game(self):
        return self.blue_o_game_shots / self.blue_o_games

    @property
    def average_shots_per_blue_d_game(self):
        return self.blue_d_game_shots / self.blue_d_games

    @property
    def average_shots_per_red_game(self):
        return self.red_shots / self.red_games

    @property
    def average_shots_per_blue_game(self):
        return self.blue_shots / self.blue_games

    @property
    def average_shots_per_offense_game(self):
        return self.offense_shots / self.offense_games

    @property
    def average_shots_per_defense_game(self):
        return self.defense_shots / self.defense_games

    @property
    def average_shots_per_game(self):
        return self.total_shots / self.total_games

    # Reset statistics:
    def reset_stats(self):
        self.elo = elo.DEFAULT_ELO
        self.mu = skill.DEFAULT_MU
        self.sigma = skill.DEFAULT_SIGMA

        # Games Played:
        self.red_o_games = 0
        self.red_d_games = 0
        self.blue_o_games = 0
        self.blue_d_games = 0
        self.total_games = 0

        # Halftimes reached:
        self.red_o_halftimes = 0
        self.red_d_halftimes = 0
        self.blue_o_halftimes = 0
        self.blue_d_halftimes = 0

        # Wins:
        self.red_o_wins = 0
        self.red_d_wins = 0
        self.blue_o_wins = 0
        self.blue_d_wins = 0

        # Shots:
        self.red_o_shots = 0
        self.red_d_shots = 0
        self.blue_o_shots = 0
        self.blue_d_shots = 0

        self.red_o_game_shots = 0
        self.red_d_game_shots = 0
        self.blue_o_game_shots = 0
        self.blue_d_game_shots = 0
