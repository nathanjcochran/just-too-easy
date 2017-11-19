import webapp2
import jinja2
import json
import skill
from google.appengine.api import images
from google.appengine.ext import ndb
from models.player import *
from models.game import *
from models.shot import *

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
        self.response.headers['Cache-Control'] = 'public, max-age=3600'
        self.response.out.write(image.data)

class RankedPlayers(webapp2.RequestHandler):
    def get(self):

        # Fetch all ranked players :
        player_query = Player.query(Player.deleted == False, Player.total_games >= 10)
        players = player_query.fetch()

        # Spit them out in a template:
        template = jinja.get_template('players.html')
        self.response.write(template.render({'title': 'Ranked', 'players':players}))

class UnrankedPlayers(webapp2.RequestHandler):
    def get(self):

        # Fetch all unranked players :
        player_query = Player.query(Player.deleted == False, Player.total_games < 10)
        players = player_query.fetch()

        # Spit them out in a template:
        template = jinja.get_template('players.html')
        self.response.write(template.render({'title': 'Unranked', 'players':players}))

class DeletedPlayers(webapp2.RequestHandler):
    def get(self):

        # Fetch all deleted players :
        player_query = Player.query(Player.deleted == True)
        players = player_query.fetch()

        # Spit them out in a template:
        template = jinja.get_template('players.html')
        self.response.write(template.render({'title': 'Hall of Fame', 'players':players}))


class NewPlayer(webapp2.RequestHandler):
    def get(self):
        template = jinja.get_template('new_player.html')
        self.response.write(template.render())

    def post(self):
        player = Player()
        player.name = self.request.get('name')

        # Fix orientation, if necessary:
        img = images.Image(self.request.get('image'))
        img.set_correct_orientation(images.CORRECT_ORIENTATION)
        
        # Resize to square (also helps reduce size, so it fits in data store):
        img.resize(width=500, height=500, crop_to_fit=True)

        image = Image()
        image.data = img.execute_transforms()
        image.put()

        player.image = image.key
        player.put()

        self.redirect('/players/unranked')

class RemovePlayer(webapp2.RequestHandler):
    def post(self):
        url_key = self.request.get('key')
        player_key = ndb.Key(urlsafe = url_key)
        player = player_key.get()
        player.deleted = True
        player.put()

        # TODO: redirect back to where they came from
        self.redirect('/players/ranked')

class RestorePlayer(webapp2.RequestHandler):
    def post(self):
        url_key = self.request.get('key')
        player_key = ndb.Key(urlsafe = url_key)
        player = player_key.get()
        player.deleted = False
        player.put()

        if player.total_games >= 10:
            self.redirect('/players/ranked')
        else:
            self.redirect('/players/unranked')

class RecalculateStats(webapp2.RequestHandler):

    def get(self):
        # Fetch all players:
        player_query = Player.query()
        players = player_query.fetch()

        for player in players:
            player.elo = 1600
            player.mu = skill.DEFAULT_MU
            player.sigma = skill.DEFAULT_SIGMA
            player.total_games = 0
            player.total_wins = 0

        player_dict = {p.key : p for p in players}

        game_query = Game.query().order(Game.timestamp)
        games = game_query.fetch()

        for game in games:
            if not game.is_complete():
                continue
            game.adjust_player_ratings(player_dict[game.red_o], player_dict[game.red_d], player_dict[game.blue_o], player_dict[game.blue_d])

        for key in player_dict:
            player_dict[key].put()

        self.response.write("Success")

class FixImages(webapp2.RequestHandler):

    def get(self):
        # Fetch all players:
        player_query = Player.query()
        players = player_query.fetch()

        for player in players:
            image = player.image.get()

            # Fix orientation, if necessary:
            img = images.Image(image.data)
            img.set_correct_orientation(images.CORRECT_ORIENTATION)

            # Resize to square (also helps reduce size, so it fits in data store):
            img.resize(width=500, height=500, crop_to_fit=True)

            # Save:
            image.data = img.execute_transforms()
            image.put()

        self.response.write("Success")

app = webapp2.WSGIApplication([
    ('/players/ranked', RankedPlayers),
    ('/players/unranked', UnrankedPlayers),
    ('/players/hall-of-fame', DeletedPlayers),
    ('/players/new', NewPlayer),
    ('/players/remove', RemovePlayer),
    ('/players/restore', RestorePlayer),
    ('/players/image', ViewImage),
    ('/players/recalc', RecalculateStats),
    ('/players/fiximages', FixImages)
], debug=True)
