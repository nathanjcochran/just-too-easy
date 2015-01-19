import json
import webapp2
import jinja2
from random import shuffle
from models import *
from google.appengine.api import memcache

GAME_LENGTH = 6

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

def entity_from_url_key(url_key):
    key = ndb.Key(urlsafe = url_key)
    return key.get()

class NewGame(webapp2.RequestHandler):
    """
    User selects 4 players to start game:
    """
    def get(self):
        players = Player.query(Player.deleted == False)
        template = jinja.get_template('new_game.html')
        self.response.write(template.render({'players':players}))

    """
    Randomly assign players' positions, create game:
    """ 
    def post(self):
        url_keys = self.request.get_all('players')

        # Incorrect number of players:
        if len(url_keys) != 4:
            players = Player.query(Player.deleted == False)
            model = {
                'players':players,
                'error':'Please select exactly 4 players'
            }

            template = jinja.get_template('new_game.html')
            self.response.write(template.render(model))
            return

        # Get players:
        player_keys = []
        for url_key in url_keys:
            player_key = ndb.Key(urlsafe = url_key)
            player_keys.append(player_key)

        # Create game:
        game = Game()
        game.initialize_random(GAME_LENGTH, player_keys)
        game.put()

        self.redirect('/game/play?key=' + game.key.urlsafe())

class AutomaticRematch(webapp2.RequestHandler):
    """
    Start a new game that is an automatic rematch of a previous game
    """
    def post(self):
        url_key = self.request.get('game')
        game_key = ndb.Key(urlsafe = url_key)
        game = game_key.get()

        winning_side = game.winning_side()

        new_game = Game()
        new_game.initialize(game.length, game.red_o, game.red_d, game.blue_o, game.blue_d)
        new_game.put()

        self.redirect('/game/play?key=' + new_game.key.urlsafe())

class PlayGame(webapp2.RequestHandler):
    """
    Play a game. Shows score and reveals scoring buttons.
    """
    def get(self):
        url_key = self.request.get('key')

        if not url_key:
            players = Player.query()
            players_dict = {p.key : p.name for p in players}

            active_games = Game.query(Game.status == GameStatus.active).order(-Game.timestamp).fetch()
            template = jinja.get_template('view_games.html')
            self.response.write(template.render({"active_games":active_games, "players":players_dict}))
            return;

        game_key = ndb.Key(urlsafe = url_key)
        game = game_key.get()

        model = {
            'game' : game,
        }

        template = jinja.get_template('play_game.html')
        self.response.write(template.render(model))

    """
    Score a point, advance the game
    """
    def post(self):
        try:
            game_url_key = self.request.get('game_key')
            if not game_url_key:
                raise Exception('Error: no game key')
            
            game_key = ndb.Key(urlsafe = game_url_key)
            if not game_key:
                raise Exception('Error: invalid game key')

            game = game_key.get()

            player_url_key = self.request.get('player_key')
            if not player_url_key:
                raise Exception('Error: no player_key')

            player_key = ndb.Key(urlsafe = player_url_key)
            if not player_key:
                raise Exception('Error: invalid player key')

            red_score = game.red_score()
            blue_score = game.blue_score()

            game.register_shot(player_key)

        except Exception, e:
            response = {
                'success' : False,
                'message' : e.args[0]
            }

            self.response.write(json.dumps(response))
            self.response.status = 200

        else:
            response = {
                'success' : True,
                'game_over' : game.status != GameStatus.active,
                'red_elo' : game.red_elo,
                'blue_elo' : game.blue_elo,
                'red_score' : len(game.red_shots),
                'blue_score' : len(game.blue_shots),
            }

            self.response.write(json.dumps(response))
            self.response.status = 200


app = webapp2.WSGIApplication([
    ('/game/new', NewGame),
    ('/game/rematch', AutomaticRematch),
    ('/game/play', PlayGame)
    ], debug=True)
