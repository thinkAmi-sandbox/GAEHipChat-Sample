#-*- coding: utf-8 -*-

import webapp2
from google.appengine.ext.webapp import template

import hipchatapiv1
import hipchatapiv2


class ApiV1(webapp2.RequestHandler):
    def get(self):
        rooms = hipchatapiv1.get_rooms()

        self.response.out.write(template.render('html/v1.html', 
                                                {'version': 'v1',
                                                 'rooms': rooms,
                                                }))

    def post(self):
        hipchatapiv1.send(self.request)

        self.response.out.write(template.render('html/post.html', 
                                                {'version': 'v1'}))



class ApiV2(webapp2.RequestHandler):
    def get(self):
        rooms = hipchatapiv2.get_rooms()

        self.response.out.write(template.render('html/v2.html', 
                                                { 'version': 'v2',
                                                  'rooms': rooms,
                                                }))


    def post(self):
        hipchatapiv2.send(self.request)

        self.response.out.write(template.render('html/post.html', 
                                                {'version': 'v2'}))
    

app = webapp2.WSGIApplication([
                                ('/v1', ApiV1),
                                ('/v2', ApiV2),
                              ],
                              debug=True)