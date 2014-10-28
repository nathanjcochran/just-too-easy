import webapp2
import jinja2
import models

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class Players(webapp2.RequestHandler):
    def get(self):
        Players

        template = jinja.get_template('players.html')
        self.response.write(template.render())

    def post(self):


app = webapp2.WSGIApplication([
    ('/', PlayGame)
], debug=True)
