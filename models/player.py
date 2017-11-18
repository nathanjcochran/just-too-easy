from google.appengine.ext import ndb
from datetime import *
import skill

class Player(ndb.Model):
    name = ndb.StringProperty(required=True)
    elo = ndb.IntegerProperty(required=True, default=1600)
    total_games = ndb.IntegerProperty(required=True, default=0)
    total_wins = ndb.IntegerProperty(required=True, default=0)
    last_played = ndb.DateTimeProperty(required=True, default=datetime.min)
    image = ndb.KeyProperty(kind='Image')
    deleted = ndb.BooleanProperty(required=True, default=False)

    # TrueSkill
    mu = ndb.FloatProperty(required=True, default=skill.DEFAULT_MU)
    sigma = ndb.FloatProperty(required=True, default=skill.DEFAULT_SIGMA)

    def win_percentage(self):
        if self.total_games > 0:
            return round(float(self.total_wins) / self.total_games * 100, 2)
        else:
            return None

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

