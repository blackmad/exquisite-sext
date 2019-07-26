from tinydb import TinyDB, Query
from flask_socketio import emit
import uuid
import time

db = TinyDB('db.json')
roomsDb = db.table('rooms')
messagesDb = db.table('messages')


def findRoom(roomId):
    Room = Query()
    roomResults = roomsDb.search(Room.id == roomId)
    if not roomResults:
        raise Exception('room %s not found' % roomId)

    room = roomResults[0]
    return room


def setParticipant(roomId, room, name, sid):
    Room = Query()
    roomsDb.update({'participant': name}, Room.id == roomId)
    setOnline(roomId, room, name, sid)


def addMessage(roomId, name, text):
    msg = {
        'roomId': roomId,
        'name': name,
        'text': text,
        'ts': time.time()
    }
    messagesDb.insert(msg)

    room = findRoom(roomId)
    story = room['story'] + ' ' + text
    Room = Query()
    roomsDb.update({'story': story}, Room.id == roomId)

def getStory(roomId):
    room = findRoom(roomId)
    return room['story']

def getMessages(roomId):
    Messages = Query()
    messages = messagesDb.search(Messages.roomId == roomId)
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
    roomsDb.insert(newRoom)
    return newRoom


def setOnline(roomId, room, name, sid):
    Room = Query()
    if name == room['creator']:
        print('setting creatorSid %s' % sid)
        roomsDb.update({'creatorSid': sid}, Room.id == roomId)
    else:
        print('setting participantSid %s' % sid)
        roomsDb.update({'participantSid': sid}, Room.id == roomId)


def setOffline(sid, cb):
    print('disconnecting sid %s' % sid)
    Room = Query()
    roomResults = roomsDb.search(
        (Room.creatorSid == sid) | (Room.participantSid == sid))
    for r in roomResults:
        if sid == r['participantSid']:
            print('sid left room %s' % r['id'])
            cb(r['participant'], r['id'])
        else:
            cb(r['creator'], r['id'])

    Room = Query()
    roomsDb.update({'creatorSid': ''}, Room.creatorSid == sid)
    roomsDb.update({'participantSid': ''}, Room.participantSid == sid)
