from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from . import database
import time
from app.main.room_utils import make_room_completions

@socketio.on('joined')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    sid = request.sid

    print('joined!!! %s' % sid)

    roomId = message['roomId']
    name = message['name']
    room = database.findRoom(roomId)
    print(room)
    if name != room['creator'] and ('participant' not in room or not room['participant']):
        print('yay they are our participant')
        database.setParticipant(roomId, room, name, sid)
        print('emitting setParticipant')
        emit('setParticipant', {'name': name}, room=roomId)
        print('emitting status')
        emit('status', {'msg': name + ' has entered the room.'}, room=roomId)
    else:
        database.setOnline(roomId, room, name, sid)
        emit('status', {'msg': name + ' has returned.'}, room=roomId)

    if 'participant' in room and name != room['participant'] and name != room['creator']:
        raise 'Hey, you are not one of the two players in this room'

    join_room(roomId)


@socketio.on('text')
def rcv_text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    roomId = message['roomId']
    name = message['name']
    text = message['text']

    database.addMessage(roomId=roomId, name=name, text=text)
    completions = make_room_completions(roomId)

    emit('message', {
        'name': name,
        'text': text,
        'completions': completions
    }, room=roomId)

# @socketio.on('left', namespace='/chat')
# def left(sid, message):
#     """Sent by clients when they leave a room.
#     A status message is broadcast to all people in the room."""
#     roomId = message['roomId']
#     name = message['name']
#     leave_room(roomId)
#     database.setOffline(sid, roomId, name)
#     emit('status', {'msg': name + ' has left the room.'}, room=roomId)


@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    print('sid disconnected: ' + sid)

    def cb(name, roomId):
        # why isn't this working
        print('trying to send out disconnect status')
        emit('status', {
             'msg': name + ' has disconnected. Maybe they will come back?'}, room=roomId)

    database.setOffline(sid, cb)
