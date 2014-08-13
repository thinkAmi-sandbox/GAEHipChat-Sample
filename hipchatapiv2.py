#-*- coding: utf-8 -*-

import json
import yaml

import webapp2
from google.appengine.ext import deferred
from google.appengine.api import urlfetch


API_ALL_ROOMS_BASE_URL = 'https://api.hipchat.com/v2/room?auth_token={token}'
API_SEND_BASE_URL = 'https://api.hipchat.com/v2/room/{id_or_name}/notification?auth_token={token}'


def load_token():
    keys = yaml.safe_load(open('api.yaml').read().decode('utf-8'))
    return keys['api_v2_account_token']


def get_rooms():
    token = load_token()
    url = API_ALL_ROOMS_BASE_URL.format(token=token)
    response = urlfetch.fetch(url, method=urlfetch.GET)
    return json.loads(response.content)


def send(request):
    roomId = request.get('roomId')
    message = request.get('message').encode('utf-8')
    deferred.defer(send_to_hipchat, roomId, message)


def send_to_hipchat(roomId, message):
    count = webapp2.get_request().headers.get('X-AppEngine-TaskRetryCount')
    if int(count) > 5:
        raise deferred.PermanentTaskFailure

    token = load_token()
    url = API_SEND_BASE_URL.format(id_or_name=roomId,
                                   token=token)

    parameter = { 'color': 'yellow',
                  'message': message,
                  'message_format': 'text'
                }
    json_body = json.dumps(parameter)

    urlfetch.fetch(url, 
                   payload=json_body, 
                   method=urlfetch.POST, 
                   headers={'Content-Type': 'application/json'})