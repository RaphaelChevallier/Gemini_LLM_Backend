import asyncio
import os
from string import ascii_uppercase

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send

import main
import vectorstore

load_dotenv('.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SOCKET_SECRET_KEY')
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

# app.route("/updateChatHistory", methods=["POST"])
# def updateMessages(): 
#     print('called')
#     data = request.form
#     user_id = data['user_id']
#     vectorstore.updateChatHistoryStore(user_id)
#     return "hello"

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
    response = main.startChat(data['userMessage'], data['userId'])
    print("data from the front end: ",str(data['userMessage']))
    print(response)
    emit('data', response) 
    asyncio.run(vectorstore.updateChatHistoryStore(data['userId']))

@socketio.on("disconnect")
def disconnected():
    session.clear()
    """event listener when client disconnects to the server"""
    print("user disconnected")
    send(f"user {request.sid} disconnected")

if(__name__) == "__main__":
    # app.run(app, debug = True, port = 5001)
    socketio.run(app, debug = True, port=5001)