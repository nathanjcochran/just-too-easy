import math

K_FACTOR  = 32.0

class EloCalculator():

    def calculate(self, avg_winner_rating, avg_loser_rating):
        winner_r = self.transform_rating(avg_winner_rating)
        loser_r = self.transform_rating(avg_loser_rating)

        self.winner_expected, self.loser_expected = self.expected_scores(winner_r, loser_r)

    def get_new_winner_rating(self, old_rating):
        return self.updated_rating(old_rating, self.winner_expected, 1)

    def get_new_loser_rating(self, old_rating):
        return self.updated_rating(old_rating, self.loser_expected, 0)

    def transform_rating(self, rating):
        return math.pow(10, (rating/400.0))

    def expected_scores(self, r1, r2):
        e1 = r1 / (r1 + r2)
        e2 = r2 / (r1 + r2)
        return e1, e2

    def updated_rating(self, r, e, s):
        return int(round(r + K_FACTOR * (s - e)))
