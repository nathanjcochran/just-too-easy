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

class Home(webapp2.RequestHandler):
    def get(self):
        self.redirect("/players")

app = webapp2.WSGIApplication([
    ('/', Home),
], debug=True)
