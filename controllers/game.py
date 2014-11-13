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
        game = entity_from_url_key(self.request.get('game_key'))
        player_key = ndb.Key(urlsafe = self.request.get('player_key'))

        # Get the actor who made the shot:
        side, position = game.side_and_position(player_key)

        # Create the shot record:
        shot = Shot(parent = game.key)
        shot.player = player_key
        shot.position = position
        shot.side = side

        # If red scored:
        if side == Side.red:
            shot.against = game.blue_d
            shot.put()
            game.red_shots.append(shot.key)

            # Mark game complete if over:
            if len(game.red_shots) >= game.length:
                game.status = GameStatus.complete

        # If blue scored:
        elif side == Side.blue:
            shot.against = game.red_d
            shot.put()
            game.blue_shots.append(shot.key)

            # Mark game complete if over:
            if len(game.blue_shots) >= game.length:
                game.status = GameStatus.complete

        game.put()

        response = {
            'success' : True,
            'game_over' : game.status != GameStatus.active,
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
