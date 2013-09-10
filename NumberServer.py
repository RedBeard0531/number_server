from google.appengine.ext import ndb
from webob.exc import HTTPNotFound, HTTPConflict

import os
import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Counter(ndb.Model):
    value = ndb.IntegerProperty(required=True)
    
    @classmethod
    def get_or_error(cls, key):
        counter = cls.get_by_id(key)
        if counter is None:
            raise HTTPNotFound("No such Counter: " + key)
        return counter

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        counters = list(Counter.query())
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(counters=counters))


class Numbers(webapp2.RequestHandler):

    @ndb.transactional
    def put(self, key):
        counter = Counter.get_by_id(key)
        if counter:
            raise HTTPConflict("Counter '" + key + "' already exists")

        counter = Counter.get_or_insert(key, value=0);
        counter.put();

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(str(counter.value))

    @ndb.transactional
    def post(self, key):
        counter = Counter.get_or_error(key)
        counter.value += 1
        counter.put();

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(str(counter.value))

    def get(self, key):
        counter = Counter.get_or_error(key)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(str(counter.value))


application = webapp2.WSGIApplication([
    (r'/', MainPage),
    (r'/number/([a-zA-Z_]+)', Numbers),
], debug=True)

