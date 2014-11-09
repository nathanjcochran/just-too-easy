import webapp2
import jinja2
from google.appengine.ext import ndb
from models import *

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class ShotTypes(webapp2.RequestHandler):
    def get(self):

        # Fetch all shot types:
        shot_type_query = ShotType.query()
        shot_types = shot_type_query.fetch()

        positions = [p for p in Position]

        model = {
            'shot_types' : shot_types,
            'positions' : positions,
        }

        # Spit them out in a template:
        template = jinja.get_template('shot_types.html')
        self.response.write(template.render(model))

class AddShotType(webapp2.RequestHandler):
    def post(self):
        shot_type = ShotType()
        shot_type.name = self.request.get('name')
        shot_type.position = Position(self.request.get('position'))
        shot_type.put()

        self.redirect('/shot_types')

class RemoveShotType(webapp2.RequestHandler):
    def post(self):
        url_key = self.request.get('key')
        shot_type_key = ndb.Key(urlsafe = url_key)
        shot_type_key.delete()

        self.redirect('/shot_types')


app = webapp2.WSGIApplication([
    ('/shot_types', ShotTypes),
    ('/shot_types/add', AddShotType),
    ('/shot_types/remove', RemoveShotType)
], debug=True)

