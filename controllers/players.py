import webapp2
import jinja2
import json
from google.appengine.ext import ndb
from models import *

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class ViewImage(webapp2.RequestHandler):
    def get(self):
        url_key = self.request.get('key')
        image_key = ndb.Key(urlsafe = url_key)
        image = image_key.get()

        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(image.data)

class Players(webapp2.RequestHandler):
    def get(self):

        # Fetch all players:
        player_query = Player.query()
        players = player_query.fetch()

        # Spit them out in a template:
        template = jinja.get_template('players.html')
        self.response.write(template.render({'players':players}))

class AddPlayer(webapp2.RequestHandler):
    def post(self):
        player = Player()
        player.name = self.request.get('name')

        image = Image()
        image.data = self.request.get('image')
        image.put()

        player.image = image.key
        player.put()

        self.redirect('/players')

class RemovePlayer(webapp2.RequestHandler):
    def post(self):
        url_key = self.request.get('key')
        player_key = ndb.Key(urlsafe = url_key)
        player_key.delete()

        self.redirect('/players')

class RecalculateStats(webapp2.RequestHandler):

    def get(self):
        # Fetch all players:
        player_query = Player.query()
        players = player_query.fetch()

        for player in players:
            player.elo = 1600
            player.total_games = 0
            player.total_wins = 0

        player_dict = {p.key : p for p in players}

        game_query = Game.query().order(Game.timestamp)
        games = game_query.fetch()

        for game in games:
            game.adjust_player_ratings(player_dict[game.red_o], player_dict[game.red_d], player_dict[game.blue_o], player_dict[game.blue_d])

        for key in player_dict:
            player_dict[key].put()

        self.response.write("Success")

app = webapp2.WSGIApplication([
    ('/players', Players),
    ('/players/add', AddPlayer),
    ('/players/remove', RemovePlayer),
    ('/players/image', ViewImage),
    ('/players/recalc', RecalculateStats),
], debug=True)

