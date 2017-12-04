import json
import webapp2
import jinja2
from random import shuffle
from models.game import *
from models.player import *
from google.appengine.api import memcache

GAME_LENGTH = 6
PAGE_SIZE = 10

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

def entity_from_url_key(url_key):
    key = ndb.Key(urlsafe = url_key)
    return key.get()

class ActiveGames(webapp2.RequestHandler):
    def get(self):
        cursor = ndb.Cursor(urlsafe=self.request.get('next'))

        games, next_cursor, more = Game.query(
            Game.status == GameStatus.active,
        ).order(
            -Game.timestamp,
        ).fetch_page(
            PAGE_SIZE,
            start_cursor=cursor,
         )
        
        next_link = None
        if next_cursor and more:
            next_link = '/games/active?next=' + next_cursor.urlsafe()

        players = Player.query()
        players_dict = {p.key : p.name for p in players}

        template = jinja.get_template('games.html')
        self.response.write(template.render({
            "title": "Active",
            "games": games,
            "next_link": next_link,
            "players": players_dict,
        }))

class CompletedGames(webapp2.RequestHandler):
    def get(self):
        cursor = ndb.Cursor(urlsafe=self.request.get('next'))

        games, next_cursor, more = Game.query(
            Game.status == GameStatus.complete
        ).order(
            -Game.timestamp,
        ).fetch_page(
            PAGE_SIZE,
            start_cursor=cursor,
        )

        next_link = None
        if next_cursor and more:
            next_link = '/games/completed?next=' + next_cursor.urlsafe()

        players = Player.query()
        players_dict = {p.key : p.name for p in players}

        template = jinja.get_template('games.html')
        self.response.write(template.render({
            "title": "Completed",
            "games":games,
            "next_link": next_link,
            "players":players_dict,
        }))

class NewGame(webapp2.RequestHandler):
    """
    User selects 4 players to start game:
    """
    def get(self):
        players = Player.query(Player.deleted == False).order(-Player.last_played, -Player.total_games)
        template = jinja.get_template('new_game.html')
        self.response.write(template.render({'players':players}))

    """
    Randomly assign players' positions, create game:
    """
    def post(self):
        url_keys = self.request.get_all('players')

        # Incorrect number of players:
        if len(url_keys) != 4:
            players = Player.query(Player.deleted == False).order(Player.name)
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
        match_mode = self.request.get("match_mode")

        game = Game()
        if match_mode == "Random":
            game.initialize_random(GAME_LENGTH, player_keys)

        if match_mode == "Matched":
            game.initialize_matched(GAME_LENGTH, player_keys)

        game.put()

        self.redirect('/games/play?key=' + game.key.urlsafe())

class Rematch(webapp2.RequestHandler):
    """
    Start a new game that is a rematch of a previous game
    """
    def post(self):
        url_key = self.request.get('game')
        game_key = ndb.Key(urlsafe = url_key)
        game = game_key.get()

        rematch_mode = self.request.get("rematch_mode")

        new_game = Game()
        if rematch_mode == "Automatic Rematch":
            new_game.initialize(game.length, game.red_o, game.red_d, game.blue_o, game.blue_d)
        elif rematch_mode == "Random Rematch":
            new_game.initialize_random(game.length, [game.red_o, game.red_d, game.blue_o, game.blue_d])
        elif rematch_mode == "Matched Rematch":
            new_game.initialize_matched(game.length, [game.red_o, game.red_d, game.blue_o, game.blue_d])
        else:
            raise "Invalid rematch mode: " + rematch_mode

        new_game.put()

        self.redirect('/games/play?key=' + new_game.key.urlsafe())

class PlayGame(webapp2.RequestHandler):
    """
    Play a game. Shows score and reveals scoring buttons.
    """
    def get(self):
        url_key = self.request.get('key')

        if not url_key:
            self.redirect('/games/active')
            return

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

            red_score = game.red_score
            blue_score = game.blue_score

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
                'game_over' : game.is_complete,
                'red_elo' : game.red_elo,
                'blue_elo' : game.blue_elo,
                'red_score' : game.red_score,
                'blue_score' : game.blue_score,
            }

            self.response.write(json.dumps(response))
            self.response.status = 200

app = webapp2.WSGIApplication([
    ('/games/active', ActiveGames),
    ('/games/completed', CompletedGames),
    ('/games/new', NewGame),
    ('/games/rematch', Rematch),
    ('/games/play', PlayGame)
    ], debug=True)
