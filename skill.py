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

def get_rating(player):
  rating = trueskill.Rating(mu=player.mu, sigma=player.sigma)
  return int(_ENV.expose(rating))
