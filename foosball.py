import webapp2
import jinja2

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class PlayGame(webapp2.RequestHandler):
    def get(self):
        values = {
            'red_o':'Jim',
            'red_d':'Nate',
            'blue_o':'Shawn',
            'blue_d':'Ben',
        }

        template = jinja.get_template('play_game.html')
        self.response.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/', PlayGame)
], debug=True)
