import webapp2
import jinja2
import models

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class Game(webapp2.RequestHandler):
    def get(self):
        values = {
            'red_o':'Jim',
            'red_d':'Nate',
            'blue_o':'Shawn',
            'blue_d':'Ben',
        }

        template = jinja.get_template('game.html')
        self.response.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/game', Game)
], debug=True)
