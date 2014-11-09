import webapp2
import jinja2
from random import shuffle
from models import *

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
        url_keys = self.request.get('players', allow_multiple=True)

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
        game_key = ndb.Key(urlsafe = url_key)
        game = game_key.get()

        shot_types = ShotType.query()

        # Lots of gets, here.  Possibly rethink:
        values = {
            'game' : game,
            'offensive_shots' : [s for s in shot_types if s.position != Position.defense],
            'defensive_shots' : [s for s in shot_types if s.position != Position.offense],
        }

        template = jinja.get_template('play_game.html')
        self.response.write(template.render(values))

    """
    Score a point, advance the game
    """
    def post(self):
        game = entity_from_url_key(self.request.get('game_key'))
        shot_type_key = ndb.Key(urlsafe = self.request.get('shot_type_key'))
        player_key = ndb.Key(urlsafe = self.request.get('player_key'))

        # Get the actor who made the shot:
        side, position = game.side_and_position(player_key)

        # Create the shot record:
        shot = Shot(ancestor = game.key)
        shot.player = player_key
        shot.position = position
        shot.side = side
        shot.shot_type = shot_type_key

        # If red scored:
        if side == Side.red:
            game.red_shots.append(shot.key)
            shot.against = game.blue_d

            # Mark game complete if over:
            if len(game.red_shots) >= game.length:
                game.status = GameStatus.complete

        # If blue scored:
        elif side == Side.blue:
            game.blue_shots.append(shot.key)
            shot.against = game.red_d

            # Mark game complete if over:
            if len(game.blue_shots) >= game.length:
                game.status = GameStatus.complete

        shot.put()
        game.put()

        self.redirect('/game/play?key=' + game.key.urlsafe())


app = webapp2.WSGIApplication([
    ('/game/new', NewGame),
    ('/game/play', PlayGame)
    ], debug=True)
