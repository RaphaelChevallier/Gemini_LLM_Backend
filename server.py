import asyncio

from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_cors import CORS

import main

load_dotenv('.env')

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SOCKET_SECRET_KEY')
# CORS(app,resources={r"/*":{"origins":"*"}})
# socketio = SocketIO(app,cors_allowed_origins="*")

# socketio.on_namespace(UserNamespace('/user_<user_id>'))
# socketio.on_namespace('user_32124312')(UserNamespace)

@app.route("/llm_server/tokenCount" , methods=["POST"])
def respondTokenCount():
    userMessage = request.json['userMessage']
    count = main.countTokens(userMessage)
    print(count.total_tokens)
    return {"total_tokens": count.total_tokens}

@app.route("/llm_server/getLLMResponse" , methods=["POST"])
def respondToUser():
    userMessage = request.json['userMessage']
    userId = request.json['userId']
    response = main.questionLLMs(userMessage, userId)
    print(response)
    return {"llmResponse": response}

# @socketio.on("connect")
# def connected():
#     session.clear()
#     """event listener when client connects to the server"""
#     print(request.sid)
#     print("client has connected")

# @socketio.on('tokenCount')
# def handle_message(data):
#     """event listener when client types a message to get current token count"""
#     response = main.countTokens(data['userMessage'])
#     emit('tokenCount', response.total_tokens)

# @socketio.on('data')
# def handle_message(data):
#     """event listener when client types a message"""
#     print("\n\n")
#     response = main.questionLLMs(data['userMessage'], data['userId'])
#     print("\n\n")
#     # print("data from the front end: ",str(data['userMessage']))
#     # print(response)
#     emit('data', response) 
#     asyncio.run(vectorstore.updateChatHistoryStore(data['userId']))

# @socketio.on("disconnect")
# def disconnected():
#     session.clear()
#     """event listener when client disconnects to the server"""
#     print("user disconnected")

if(__name__) == "__main__":
    # socketio.run(app, host='0.0.0.0', port=5001)
    # socketio.run(app, debug = True, port=5001)
    app.run(debug=True, port=5001)