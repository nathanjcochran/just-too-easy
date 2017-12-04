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

    # Is Ranked:
    @property
    def is_ranked(self):
        return self.total_games >= RANKED_THRESHOLD

    # Games played:
    total_games = ndb.IntegerProperty(required=True, default=0)

    # NOTE: "o" and "d" refer to the *starting position* of the player
    red_o_games = ndb.IntegerProperty(required=True, default=0)
    red_d_games = ndb.IntegerProperty(required=True, default=0)
    blue_o_games = ndb.IntegerProperty(required=True, default=0)
    blue_d_games = ndb.IntegerProperty(required=True, default=0)

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

    @property
    def percent_red_o_games(self):
        return self.red_o_games / float(self.total_games) * 100

    @property
    def percent_red_d_games(self):
        return self.red_d_games / float(self.total_games) * 100

    @property
    def percent_blue_o_games(self):
        return self.blue_o_games / float(self.total_games) * 100

    @property
    def percent_blue_d_games(self):
        return self.blue_d_games / float(self.total_games) * 100

    @property
    def percent_red_games(self):
        return self.red_games / float(self.total_games) * 100

    @property
    def percent_blue_games(self):
        return self.blue_games / float(self.total_games) * 100

    @property
    def percent_offense_games(self):
        return self.offense_games / float(self.total_games) * 100

    @property
    def percent_defense_games(self):
        return self.defense_games / float(self.total_games) * 100

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

    # Halftime Rate:
    @property
    def red_o_halftime_rate(self):
        if self.red_o_games > 0:
            return round(self.red_o_halftimes / float(self.red_o_games) * 100, 2)
        else:
            return None

    @property
    def red_d_halftime_rate(self):
        if self.red_d_games > 0:
            return round(self.red_d_halftimes / float(self.red_d_games) * 100, 2)
        else:
            return None

    @property
    def blue_o_halftime_rate(self):
        if self.blue_o_games > 0:
            return round(self.blue_o_halftimes / float(self.blue_o_games) * 100, 2)
        else:
            return None

    @property
    def blue_d_halftime_rate(self):
        if self.blue_d_games > 0:
            return round(self.blue_d_halftimes / float(self.blue_d_games) * 100, 2)
        else:
            return None

    @property
    def blue_halftime_rate(self):
        if self.blue_games > 0:
            return round(self.blue_halftimes / float(self.blue_games) * 100, 2)
        else:
            return None

    @property
    def red_halftime_rate(self):
        if self.red_games > 0:
            return round(self.red_halftimes / float(self.red_games) * 100, 2)
        else:
            return None

    @property
    def defense_halftime_rate(self):
        if self.defense_games > 0:
            return round(self.defense_halftimes / float(self.defense_games) * 100, 2)
        else:
            return None

    @property
    def offense_halftime_rate(self):
        if self.offense_games > 0:
            return round(self.offense_halftimes / float(self.offense_games) * 100, 2)
        else:
            return None

    @property
    def halftime_rate(self):
        if self.total_games > 0:
            return round(self.total_halftimes / float(self.total_games) * 100, 2)
        else:
            return None

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

    # Win Rates:
    @property
    def red_o_win_rate(self):
        if self.red_o_games > 0:
            return round(float(self.red_o_wins) / self.red_o_games * 100, 2)
        else:
            return None

    @property
    def red_d_win_rate(self):
        if self.red_d_games > 0:
            return round(float(self.red_d_wins) / self.red_d_games * 100, 2)
        else:
            return None

    @property
    def blue_o_win_rate(self):
        if self.blue_o_games > 0:
            return round(float(self.blue_o_wins) / self.blue_o_games * 100, 2)
        else:
            return None

    @property
    def blue_d_win_rate(self):
        if self.blue_d_games > 0:
            return round(float(self.blue_d_wins) / self.blue_d_games * 100, 2)
        else:
            return None

    @property
    def red_win_rate(self):
        if self.red_games > 0:
            return round(float(self.red_wins) / self.red_games * 100, 2)
        else:
            return None

    @property
    def blue_win_rate(self):
        if self.blue_games > 0:
            return round(float(self.blue_wins) / self.blue_games * 100, 2)
        else:
            return None

    @property
    def offense_win_rate(self):
        if self.offense_games > 0:
            return round(float(self.offense_wins) / self.offense_games * 100, 2)
        else:
            return None

    @property
    def defense_win_rate(self):
        if self.defense_games > 0:
            return round(float(self.defense_wins) / self.defense_games * 100, 2)
        else:
            return None

    @property
    def win_rate(self):
        if self.total_games > 0:
            return round(float(self.total_wins) / self.total_games * 100, 2)
        else:
            return None

    # Positions held:
    # NOTE: "o" and "d" refer to games in which that offense/defense
    # position was achieved/held, no matter what the starting position
    @property
    def red_o_positions(self):
        return self.red_o_games + self.red_d_halftimes

    @property
    def red_d_positions(self):
        return self.red_d_games + self.red_o_halftimes

    @property
    def blue_o_positions(self):
        return self.blue_o_games + self.blue_d_halftimes

    @property
    def blue_d_positions(self):
        return self.blue_d_games + self.blue_o_halftimes

    @property
    def red_positions(self):
        return self.red_o_games + self.red_d_halftimes

    @property
    def blue_positions(self):
        return self.blue_o_games + self.blue_d_halftimes

    @property
    def offense_positions(self):
        return self.red_o_positions + self.blue_o_positions

    @property
    def defense_positions(self):
        return self.red_d_positions + self.blue_d_positions

    @property
    def total_positions(self):
        return self.red_positions + self.blue_positions

    @property
    def percent_red_o_positions(self):
        return self.red_o_positions / float(self.total_positions) * 100

    @property
    def percent_red_d_positions(self):
        return self.red_d_positions / float(self.total_positions) * 100

    @property
    def percent_blue_o_positions(self):
        return self.blue_o_positions / float(self.total_positions) * 100

    @property
    def percent_blue_d_positions(self):
        return self.blue_d_positions / float(self.total_positions) * 100

    @property
    def percent_red_positions(self):
        return self.red_positions / float(self.total_positions) * 100

    @property
    def percent_blue_positions(self):
        return self.blue_positions / float(self.total_positions) * 100

    @property
    def percent_offense_positions(self):
        return self.offense_positions / float(self.total_positions) * 100

    @property
    def percent_defense_positions(self):
        return self.defense_positions / float(self.total_positions) * 100

    # Shots:
    # NOTE: These are the total number of shots *from the given
    # offense/defense position*
    red_o_shots = ndb.IntegerProperty(required=True, default=0)
    red_d_shots = ndb.IntegerProperty(required=True, default=0)
    blue_o_shots = ndb.IntegerProperty(required=True, default=0)
    blue_d_shots = ndb.IntegerProperty(required=True, default=0)

    @property
    def red_shots(self):
        return self.red_o_shots + self.red_d_shots

    @property
    def blue_shots(self):
        return self.blue_o_shots + self.blue_d_shots

    @property
    def offense_shots(self):
        return self.red_o_shots + self.blue_o_shots

    @property
    def defense_shots(self):
        return self.red_d_shots + self.blue_d_shots

    @property
    def total_shots(self):
        return self.red_shots + self.blue_shots

    # Average Shots Per Game:
    @property
    def average_red_o_shots_per_game(self):
        if self.red_o_games > 0:
            return round(float(self.red_o_shots) / self.red_games, 2)
        else:
            return None

    @property
    def average_red_d_shots_per_game(self):
        if self.red_d_games > 0:
            return round(float(self.red_d_shots) / self.red_games, 2)
        else:
            return None

    @property
    def average_blue_o_shots_per_game(self):
        if self.blue_o_games > 0:
            return round(float(self.blue_o_shots) / self.blue_games, 2)
        else:
            return None

    @property
    def average_blue_d_shots_per_game(self):
        if self.blue_d_games > 0:
            return round(float(self.blue_d_shots) / self.blue_games, 2)
        else:
            return None

    @property
    def average_red_shots_per_game(self):
        if self.red_games > 0:
            return round(float(self.red_shots) / self.red_games, 2)
        else:
            return None

    @property
    def average_blue_shots_per_game(self):
        if self.blue_games > 0:
            return round(float(self.blue_shots) / self.blue_games, 2)
        else:
            return None

    @property
    def average_offense_shots_per_game(self):
        if self.offense_games > 0:
            return round(float(self.offense_shots) / self.offense_games, 2)
        else:
            return None

    @property
    def average_defense_shots_per_game(self):
        if self.defense_games > 0:
            return round(float(self.defense_shots) / self.defense_games, 2)
        else:
            return None

    @property
    def average_shots_per_game(self):
        if self.total_games > 0:
            return round(float(self.total_shots) / self.total_games, 2)
        else:
            return None

    # NOTE: These are the total number of shots in games where
    # the player *started in the given offense/defense position*
    red_o_start_shots = ndb.IntegerProperty(required=True, default=0)
    red_d_start_shots = ndb.IntegerProperty(required=True, default=0)
    blue_o_start_shots = ndb.IntegerProperty(required=True, default=0)
    blue_d_start_shots = ndb.IntegerProperty(required=True, default=0)

    @property
    def offense_start_shots(self):
        return self.red_o_start_shots + self.blue_o_start_shots

    @property
    def defense_start_shots(self):
        return self.red_d_start_shots + self.blue_d_start_shots

    ###

    @property
    def average_red_o_start_shots_per_game(self):
        if self.red_o_games > 0:
            return round(float(self.red_o_start_shots) / self.red_o_games, 2)
        else:
            return None

    @property
    def average_red_d_start_shots_per_game(self):
        if self.red_d_games > 0:
            return round(float(self.red_d_start_shots) / self.red_d_games, 2)
        else:
            return None

    @property
    def average_blue_o_start_shots_per_game(self):
        if self.blue_o_games > 0:
            return round(float(self.blue_o_start_shots) / self.blue_o_games, 2)
        else:
            return None

    @property
    def average_blue_d_start_shots_per_game(self):
        if self.blue_d_games > 0:
            return round(float(self.blue_d_start_shots) / self.blue_d_games, 2)
        else:
            return None

    @property
    def average_offense_start_shots_per_game(self):
        if self.offense_games > 0:
            return round(float(self.offense_start_shots) / self.offense_games, 2)
        else:
            return None

    @property
    def average_defense_start_shots_per_game(self):
        if self.defense_games > 0:
            return round(float(self.defense_start_shots) / self.defense_games, 2)
        else:
            return None

    # Reset statistics:
    def reset_stats(self):
        self.elo = elo.DEFAULT_ELO
        self.mu = skill.DEFAULT_MU
        self.sigma = skill.DEFAULT_SIGMA

        # Games Played:
        self.total_games = 0
        self.red_o_games = 0
        self.red_d_games = 0
        self.blue_o_games = 0
        self.blue_d_games = 0

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

        self.red_o_start_shots = 0
        self.red_d_start_shots = 0
        self.blue_o_start_shots = 0
        self.blue_d_start_shots = 0
