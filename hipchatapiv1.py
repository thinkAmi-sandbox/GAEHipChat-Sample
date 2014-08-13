#-*- coding: utf-8 -*-

import json
import yaml

import webapp2
from google.appengine.ext import deferred
from google.appengine.api import urlfetch


API_ALL_ROOMS_BASE_URL = 'https://api.hipchat.com/v1/rooms/list?format=json&auth_token={token}'
API_SEND_BASE_URL = 'https://api.hipchat.com/v1/rooms/message?format=json&auth_token={token}'
API_SEND_BASE_PARAMETER = 'room_id={roomId}&from={user}&message={message}&color={color}'
SENDER_NAME = 'GAE'


def load_token():
    keys = yaml.safe_load(open('api.yaml').read().decode('utf-8'))
    return keys['api_v1_admin_token']


def get_rooms():
    token = load_token()
    url = API_ALL_ROOMS_BASE_URL.format(token=token)
    response = urlfetch.fetch(url, method=urlfetch.GET)
    return json.loads(response.content)


def send(request):
    # requestオブジェクトを渡してもdefer()で呼ばれる先ではウマイこと動作しないため、
    # (Can't pickle <class 'threading._RLock'>: it's not the same object as threading._RLock)
    # それぞれ引数として用意しておく
    roomId = request.get('roomId')
    message = request.get('message').encode('utf-8')
    deferred.defer(send_to_hipchat, roomId, message)


# deferred.deferにより、Taskとして非同期で実行
def send_to_hipchat(roomId, message):
    # リトライの上限を設定しとく
    count = webapp2.get_request().headers.get('X-AppEngine-TaskRetryCount')
    if int(count) > 5:
        raise deferred.PermanentTaskFailure

    token = load_token()
    url = API_SEND_BASE_URL.format(token=token)
    parameter = API_SEND_BASE_PARAMETER.format(roomId=roomId,
                                               user=SENDER_NAME,
                                               message=message,
                                               color='purple')

    urlfetch.fetch(url, payload=parameter, method=urlfetch.POST)