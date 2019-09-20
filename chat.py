#!/bin/env python
from app import create_app, socketio

app = create_app(debug=True)
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
