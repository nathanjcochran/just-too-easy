from lib import trueskill

import math

DEFAULT_MU = 1000.
DEFAULT_SIGMA = DEFAULT_MU / 3
DEFAULT_BETA = DEFAULT_SIGMA / 2
DEFAULT_TAU = DEFAULT_SIGMA * .01
DEFAULT_DRAW = 0

_ENV = trueskill.TrueSkill(
    mu=DEFAULT_MU,
    sigma=DEFAULT_SIGMA,
    beta=DEFAULT_BETA,
    tau=DEFAULT_TAU,
    draw_probability=DEFAULT_DRAW)

def calculate_rating(mu, sigma):
    rating = trueskill.Rating(mu=mu, sigma=sigma)
    return int(_ENV.expose(rating))

def calculate_quality(red, blue):
    red_ratings = tuple(trueskill.Rating(p.mu, p.sigma) for p in red)
    blue_ratings = tuple(trueskill.Rating(p.mu, p.sigma) for p in blue)

    return int(_ENV.quality([red_ratings, blue_ratings]) * 100)

def get_rating(player):
    rating = trueskill.Rating(mu=player.mu, sigma=player.sigma)
    return int(_ENV.expose(rating))

def update_ratings(winners, losers):
    winner_ratings = tuple(trueskill.Rating(p.mu, p.sigma) for p in winners)
    loser_ratings = tuple(trueskill.Rating(p.mu, p.sigma) for p in losers)

    new_ratings = _ENV.rate([winner_ratings, loser_ratings], ranks=[0, 1])

    return new_ratings[0], new_ratings[1]
