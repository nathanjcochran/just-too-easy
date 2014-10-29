import webapp2
import jinja2
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

        self.redirect('/admin/players')

class RemovePlayer(webapp2.RequestHandler):
    def post(self):
        url_key = self.request.get('key')
        player_key = ndb.Key(urlsafe = url_key)
        player_key.delete()

        self.redirect('/admin/players')

app = webapp2.WSGIApplication([
    ('/admin/players', Players),
    ('/admin/players/add', AddPlayer),
    ('/admin/players/remove', RemovePlayer),
    ('/admin/image', ViewImage)
    ], debug=True)
