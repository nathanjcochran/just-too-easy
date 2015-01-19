import math

K_FACTOR  = 32.0

def calculate(winner_rating, loser_rating):
    winner_r = transform_rating(winner_rating)
    loser_r = transform_rating(loser_rating)

    winner_expected, loser_expected = expected_scores(winner_r, loser_r)
    return point_diff(winner_expected, 1), point_diff(loser_expected, 0)

def transform_rating(rating):
    return math.pow(10, (rating/400.0))

def expected_scores(r1, r2):
    e1 = r1 / (r1 + r2)
    e2 = r2 / (r1 + r2)
    return e1, e2

def point_diff(e, s):
    return int(round(K_FACTOR * (s - e)))
