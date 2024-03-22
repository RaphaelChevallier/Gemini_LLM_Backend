import asyncio
import os
from string import ascii_uppercase

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_socketio import (Namespace, SocketIO, emit, join_room, leave_room,
                            send)

import main
import vectorstore

load_dotenv('.env')
# class UserNamespace(Namespace):
#     def on_connect(self):
#         print("here we connected")
#         self.user_id = request.sid  # Use socket ID for identification
#         self.namespace = f"/user_{self.user_id}"  # Construct unique namespace name
#         print(f"Client connected to namespace: {self.namespace}")

#         # Initialize user data (if needed)
#         self.user_data = {'current_chat' : llm_builds.MainAgentModel.start_chat()}

#         # Retrieve pre-existing session data (optional)
#         self.user_data.update(session.get(self.user_id, {}))  # Load from session

#         # Set session data (optional)
#         session[self.user_id] = self.user_data

#     def on_data(self, data):
#         response = main.startChat(data['userMessage'], data['userId'])
#         print("data from the front end: ", str(data['userMessage']))
#         print(response)
#         self.emit('data', response)
#         asyncio.run(vectorstore.updateChatHistoryStore(data['userId']))
        
#     def on_disconnect(self):
#         print(f"Client disconnected from namespace: {self.namespace}")
#         socketio.disconnect(self.sid)

#         # Clear session data (optional)
#         del session[self.user_id]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SOCKET_SECRET_KEY')
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

# socketio.on_namespace(UserNamespace('/user_<user_id>'))
# socketio.on_namespace('user_32124312')(UserNamespace)


@socketio.on("connect")
def connected():
    session.clear()
    """event listener when client connects to the server"""
    print(request.sid)
    print("client has connected")

@socketio.on('tokenCount')
def handle_message(data):
    """event listener when client types a message to get current token count"""
    response = main.countTokens(data['userMessage'])
    emit('tokenCount', response.total_tokens)

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("\n\n")
    response = main.questionLLMs(data['userMessage'], data['userId'])
    print("\n\n")
    # print("data from the front end: ",str(data['userMessage']))
    # print(response)
    emit('data', response) 
    asyncio.run(vectorstore.updateChatHistoryStore(data['userId']))

@socketio.on("disconnect")
def disconnected():
    session.clear()
    """event listener when client disconnects to the server"""
    print("user disconnected")

if(__name__) == "__main__":
    # socketio.run(app, debug = False, port=5001)
    socketio.run(app, debug = True, port=5001)