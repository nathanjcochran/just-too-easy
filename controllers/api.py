import json
import webapp2
import jinja2
from random import shuffle
from models import *

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class Fetch(webapp2.RequestHandler):
    def get(self):
        players = {p.key : p for p in Player.query().fetch()}
        shots = {s.key : {
                'player' : players[s.player].name,
                'position' : str(s.position),
                'side' : str(s.side),
                'against' : players[s.against].name,
                'timestamp' : str(s.timestamp)
            } for s in Shot.query().fetch()
        }
        games = Game.query().fetch()

        results = []
        for game in games:
            result = {
                'length' : game.length,
                'status' : str(game.status),
                'timestamp' : str(game.timestamp),
                'red_o' : players[game.red_o].name,
                'red_d' : players[game.red_d].name,
                'blue_o' : players[game.blue_o].name,
                'blue_d' : players[game.blue_d].name,
                'red_score' : len(game.red_shots),
                'red_shots' : [shots[s] for s in game.red_shots],
                'blue_score' : len(game.blue_shots),
                'blue_shots' : [shots[s] for s in game.blue_shots]
            }
            results.append(result)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'games': results}, sort_keys=True, indent=3))


app = webapp2.WSGIApplication([
    ('/api/fetch', Fetch),
    ], debug=True)
