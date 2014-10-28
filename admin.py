import webapp2
import jinja2
from google.appengine.ext import ndb
from models import *

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

#class ViewImage(webapp2.RequestHandler):
#    def get(self):
#        key - self.request.get()

class Players(webapp2.RequestHandler):
    def get(self):

        # Fetch all players:
        player_query = Player.query()
        players = player_query.fetch()

        # Spit them out in a template:
        template = jinja.get_template('players.html')
        self.response.write(template.render({'players':players}))

    def post(self):
        player = Player()
        player.name = self.request.get('name')

        image = Image()
        image.data = self.request.get('image')
        image.put()

        player.image = image.key
        player.put()

        self.redirect('/admin/players')



app = webapp2.WSGIApplication([
    ('/admin/players', Players)
], debug=True)
