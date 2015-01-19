import math
from models import *

K_FACTOR  = 32.0

class EloCalculator():

    def calculate(self, winner_rating, loser_rating):
        winner_r = self.transform_rating(winner_rating)
        loser_r = self.transform_rating(loser_rating)

        winner_expected, loser_expected = self.expected_scores(winner_r, loser_r)
        return self.point_diff(winner_expected, 1), self.point_diff(loser_expected, 0)

    def transform_rating(self, rating):
        return math.pow(10, (rating/400.0))

    def expected_scores(self, r1, r2):
        e1 = r1 / (r1 + r2)
        e2 = r2 / (r1 + r2)
        return e1, e2

    def point_diff(self, e, s):
        return int(round(K_FACTOR * (s - e)))
