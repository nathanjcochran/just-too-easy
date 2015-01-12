import math

K_FACTOR  = 32.0

def elo_score(rating1, rating2, score1, score2):
    r1 = transform_rating(rating1)
    r2 = transform_rating(rating2)

    e1, e2 = expected_scores(r1, r2)

    new_r1 = updated_rating(rating1, e1, score1)
    new_r2 = updated_rating(rating2, e2, score2)

    return new_r1, new_r2

def transform_rating(rating):
    return math.pow(10, (rating/400.0))

def expected_scores(r1, r2):
    e1 = r1 / (r1 + r2)
    e2 = r2 / (r1 + r2)
    return e1, e2

def updated_rating(r, e, s):
    return int(round(r + K_FACTOR * (s - e)))
