# https://realpython.com/python-redis/

from flask_socketio import emit
import uuid
import time

import os
import redis
import pickle

r = redis.from_url(os.environ.get("REDIS_URL"), charset="utf-8", decode_responses=True)

def roomKey(roomId):
    return 'room:' + roomId

def messagePrefixKey(roomId):
    return 'messages:' + roomId

def messageKey(roomId, ts):
    return 'messages:' + roomId + ':' + str(ts)

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
    ts = time.time()
    msg = {
        'roomId': roomId,
        'name': name,
        'text': text,
        'ts': ts
    }
    print('trying to write message: %s', messageKey(roomId, ts))
    r.hmset(messageKey(roomId, ts), msg)

    room = findRoom(roomId)
    story = room['story'] + ' ' + text
    r.hset(roomKey(roomId), 'story', story)


def getStory(roomId):
    room = findRoom(roomId)
    return room['story']


def getMessages(roomId):
    print('scanning for %s' % messagePrefixKey(roomId))
    keys = [e for e in r.scan_iter(messagePrefixKey(roomId) + '*')]
    messages = [r.hgetall(k) for k in keys]
    print('messages', messages)
    if not messages:
      return []
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
    presence = r.hgetall(sidKey(sid))
    if not presence:
      return
    
    if presence['role'] == 'participant':
      r.hset(roomKey(presence['roomId']), 'participantSid', '')
    else:
      r.hset(roomKey(presence['roomId']), 'creatorSid', '')
