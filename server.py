import os
import random
from string import ascii_uppercase

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send

import main

load_dotenv('.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SOCKET_SECRET_KEY')
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

@socketio.on("connect")
def connected():
    session.clear()
    """event listener when client connects to the server"""
    print(request.sid)
    print("client has connected")
    send({"data":f"id: {request.sid} is connected"})

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    response = main.startChat(data)
    print("data from the front end: ",str(data))
    print(response)
    emit('data', response) 

@socketio.on("disconnect")
def disconnected():
    session.clear()
    """event listener when client disconnects to the server"""
    print("user disconnected")
    send(f"user {request.sid} disconnected")

if(__name__) == "__main__":
    # app.run(app, debug = True, port = 5001)
    socketio.run(app, debug = True, port=5001)