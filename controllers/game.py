import webapp2
import jinja2
from random import shuffle
from models import *

GAME_LENGTH = 6

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

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
        players = []
        for url_key in url_keys:
            player_key = ndb.Key(urlsafe = url_key)
            player = player_key.get()
            players.append(player)

        # Randomize
        shuffle(players)

        # Create game:
        game = Game()
        game.length = GAME_LENGTH
        game.status = GameStatus.active
        game.red_offense = players[0].key
        game.red_defense = players[1].key
        game.blue_offense = players[2].key
        game.blue_defense = players[3].key
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

        # Lots of gets, here.  Possibly rethink:
        values = {
                'red_o' : game.red_offense.get(),
                'red_d' : game.red_defense.get(),
                'blue_o' : game.blue_offense.get(),
                'blue_d' : game.blue_defense.get()
                }

        template = jinja.get_template('play_game.html')
        self.response.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/game/new', NewGame),
    ('/game/play', PlayGame)
    ], debug=True)
