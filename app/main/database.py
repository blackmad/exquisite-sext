# https://realpython.com/python-redis/

from flask_socketio import emit
import uuid
import time

import os
import redis

r = redis.from_url(os.environ.get("REDIS_URL"), charset="utf-8", decode_responses=True)

def roomKey(roomId):
    return 'room:' + roomId


def messageKey(roomId):
    return 'messages:' + roomId

def sidKey(sid):
    return 'sid:' + sid


def findRoom(roomId):
    room = r.hgetall(roomKey(roomId))
    print(room)
    if not room:
        raise Exception('room %s not found' % roomId)

    return room


def setParticipant(roomId, room, name, sid):
    r.hset(roomKey(roomId), 'participant', name)
    setOnline(roomId, room, name, sid)


def addMessage(roomId, name, text):
    msg = {
        'roomId': roomId,
        'name': name,
        'text': text,
        'ts': time.time()
    }
    r.lpush(messageKey(roomId), msg)

    room = findRoom(roomId)
    story = room['story'] + ' ' + text
    r.hset(roomKey(roomId), 'story', story)


def getStory(roomId):
    room = findRoom(roomId)
    return room['story']


def getMessages(roomId):
    messages = r.get(messageKey(roomId))
    return messages


def createRoom(creator, initialPrompt):
    newId = str(uuid.uuid1())

    newRoom = {
        'creator': creator,
        'initialPrompt': initialPrompt,
        'story': initialPrompt,
        'ts': time.time(),
        'id': newId
    }
    r.hmset(roomKey(newId), newRoom)
    return newRoom


def setOnline(roomId, room, name, sid):
    if name == room['creator']:
        print('setting creatorSid %s' % sid)
        r.hset(roomKey(roomId), 'creatorSid', sid)
        r.hmset(sidKey(sid), {
          'roomId': roomId,
          'role': 'creator'
        })
    else:
        print('setting participantSid %s' % sid)
        r.hset(roomKey(roomId), 'participantSid', sid)
        r.hmset(sidKey(sid), {
          'roomId': roomId,
          'role': 'participant'
        })


def setOffline(sid, cb):
    print('disconnecting sid %s' % sid)
    presence = r.getall(sidKey(sid))
    if not presence:
      return
    
    if presence['role'] == 'participant':
      r.hset(roomKey(presence['roomId']), 'participantSid', None)
    else:
      r.hset(roomKey(presence['roomId']), 'creatorSid', None)
