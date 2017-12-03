from google.appengine.ext import ndb
from datetime import *
import skill

RANKED_THRESHOLD = 10 # Number of games you have to play to be ranked

class Image(ndb.Model):
    data = ndb.BlobProperty(required=True)

class Player(ndb.Model):
    name = ndb.StringProperty(required=True)
    last_played = ndb.DateTimeProperty(required=True, default=datetime.min)
    image = ndb.KeyProperty(kind='Image')
    deleted = ndb.BooleanProperty(required=True, default=False)

    # Stats:
    total_games = ndb.IntegerProperty(required=True, default=0)
    total_wins = ndb.IntegerProperty(required=True, default=0)

    # Elo:
    elo = ndb.IntegerProperty(required=True, default=1600)

    # TrueSkill
    mu = ndb.FloatProperty(required=True, default=skill.DEFAULT_MU)
    sigma = ndb.FloatProperty(required=True, default=skill.DEFAULT_SIGMA)

    # Shots:
    total_red_o_shots = ndb.IntegerProperty(required=True, default=0)
    total_red_d_shots = ndb.IntegerProperty(required=True, default=0)
    total_blue_o_shots = ndb.IntegerProperty(required=True, default=0)
    total_blue_d_shots = ndb.IntegerProperty(required=True, default=0)

    def win_percentage(self):
        if self.total_games > 0:
            return round(float(self.total_wins) / self.total_games * 100, 2)
        else:
            return None
    
    def total_shots(self):
        return self.total_red_o_shots + self.total_red_d_shots + self.total_blue_o_shots + self.total_blue_d_shots

    def is_ranked(self):
        return self.total_games >= RANKED_THRESHOLD

    def trueskill_rating(self):
        return skill.get_rating(self)

    def trueskill_gain(self, teammate, opponents):
        ratings = skill.update_ratings((self, teammate), opponents)[0][0]
        rating = skill.calculate_rating(ratings.mu, ratings.sigma)

        return rating - self.trueskill_rating()

    def trueskill_loss(self, teammate, opponents):
        ratings = skill.update_ratings(opponents, (self, teammate))[1][0]
        rating = skill.calculate_rating(ratings.mu, ratings.sigma)

        return self.trueskill_rating() - rating

