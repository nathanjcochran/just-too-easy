import webapp2
import jinja2

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./views'),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

class Home(webapp2.RequestHandler):
    def get(self):
        values = {
            'text':'Hello world!'
        }

        template = jinja.get_template('home.html')
        self.response.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/', Home)
], debug=True)
