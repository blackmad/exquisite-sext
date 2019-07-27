from flask import session, redirect, url_for, render_template, request, send_from_directory
from . import main

from flask import jsonify
from . import database
from app.main.room_utils import make_room_completions

print('loading markov ...')
from app.main import markov
print('done loading!!!!')

@main.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@main.route('/')
def send_index():
    prompt = ' '.join(markov.models['bdsm'].make_sentence().split(' ')[:5])
    return render_template('index.html', prompt=prompt)


@main.route('/room/<id>')
def send_room(id):
    room = database.findRoom(id)
    print(room)
    messages = database.getMessages(id)
    completions = {'completions': make_room_completions(id)}

    print(messages)

    return render_template('room.html', roomId=id, room=room, messages={'messages': messages}, completions=completions)

# @main.route('/api/story/<id>')
# def storyRoom():
#   Room = Query()
#   roomResults = roomsDb.search(Room.id == id)
#   if not roomResults:
#     raise Exception('room %s not found' % id)

#   room = roomResults[0]
#   Messages = Query()
#   messages = messagesDb.search(Messages.roomId == id)
#   return jsonify({
#     'room': room,
#     'messages': messages
#   })


@main.route('/api/createStory', methods=['POST'])
def createRoom():
    initialPrompt = request.form.get('initialPrompt')
    if not initialPrompt:
        raise Exception('missing initialPrompt')

    newRoom = database.createRoom(
        creator=request.form.get('name'),
        initialPrompt=initialPrompt
    )

    return jsonify({
        'room': newRoom
    })
