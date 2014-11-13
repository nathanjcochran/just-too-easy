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
        players = Player.query()
        template = jinja.get_template('new_game.html')
        self.response.write(template.render({'players':players}))

    """
    Randomly assign players' positions, create game:
    """ 
    def post(self):
        url_keys = self.request.get_all('players')

        # Incorrect number of players:
        if len(url_keys) != 4:
            players = Player.query()
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

        # Randomize
        shuffle(player_keys)

        # Create game:
        game = Game()
        game.length = GAME_LENGTH
        game.status = GameStatus.active
        game.red_o = player_keys[0]
        game.red_d = player_keys[1]
        game.blue_o = player_keys[2]
        game.blue_d = player_keys[3]

        # Persist it:
        game.put()

        self.redirect('/game/play?key=' + game.key.urlsafe())

class PlayGame(webapp2.RequestHandler):
    """
    Play a game.  Shows score and reveals scoring buttons.
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

            half_time = None
            message = None
            if (game.blue_score() == game.length / 2) and (game.blue_score() == blue_score + 1):
                half_time = Side.blue
                message = "Blue half-time!"
            elif (game.red_score() == game.length / 2) and (game.red_score() == red_score + 1):
                half_time = Side.red
                message = "Red half-time!"

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
                'message' : message,
                'game_over' : game.status != GameStatus.active,
                'half_time' : str(half_time),
                'red_score' : len(game.red_shots),
                'red_score_percentage' : game.red_score_percentage(),
                'blue_score' : len(game.blue_shots),
                'blue_score_percentage' : game.blue_score_percentage()
            }

            self.response.write(json.dumps(response))
            self.response.status = 200


app = webapp2.WSGIApplication([
    ('/game/new', NewGame),
    ('/game/play', PlayGame)
    ], debug=True)
