import base64
import hashlib
import hmac
import json
import os
import shelve
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS

import mockInterviewMain

load_dotenv('.env')

def create_token(data, secret):
    # Assume data is a dictionary containing your payload
    payload = json.dumps(data).encode('utf-8')
    # Create a new HMAC object using a secret key and SHA-256
    signature = hmac.new(secret, payload, hashlib.sha256).digest()
    # Encode the payload and signature to make them URL-safe
    encoded_payload = base64.urlsafe_b64encode(payload).decode('utf-8')
    encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8')
    # Return the token format as 'payload.signature'
    return f"{encoded_payload}.{encoded_signature}"

def verify_token(token, secret):
    # Split the token into payload and signature
    encoded_payload, encoded_signature = token.split('.')
    # Decode from base64
    payload = base64.urlsafe_b64decode(encoded_payload.encode('utf-8'))
    signature = base64.urlsafe_b64decode(encoded_signature.encode('utf-8'))
    # Calculate HMAC on the payload using the shared secret
    expected_signature = hmac.new(secret, payload, hashlib.sha256).digest()
    # Compare the signatures securely
    if hmac.compare_digest(expected_signature, signature):
        # If they match, decode and return the payload
        return json.loads(payload.decode('utf-8'))
    else:
        return None

app = Flask(__name__)
CORS(app)

@app.route("/ai/generateUUID" , methods=["GET"])
def generateToken():
    # Create token
    data = {'id': uuid.uuid4().hex, 'timestamp': datetime.now().timestamp()}
    token = create_token(data, os.getenv('TOKEN_SECRET_SECURE').encode('utf-8'))
    print("Generated Token:", token)
    sh = shelve.open("sessions")
    sh[token] = {'startTime': datetime.now()}
    sh.close()
    return {'sessionId': token}


@app.route("/ai/startInterview" , methods=["POST"])
def startInterview():
    codeLanguage = request.json['codeLanguage']
    currentAssesmentDescription = request.json['currentAssesmentDescription']
    email = request.json['email']
    sessionId = request.json['sessionId']
    # Verify token
    decoded_data = verify_token(sessionId, os.getenv('TOKEN_SECRET_SECURE').encode('utf-8'))
    if decoded_data:
        print("Token is valid, data:", decoded_data)
        print(f"Starting the interview with {sessionId}!")
        mockInterviewMain.startLLMInterview(currentAssesmentDescription, email, codeLanguage, sessionId)
        return {"startInterview": True}
    else:
        print("Invalid token or corrupted data")
        return {"startInterview": False}

@app.route("/ai/endInterview" , methods=["POST"])
def endInterview():
    sessionId = request.json['sessionId']
    print(sessionId)
    # Verify token
    decoded_data = verify_token(sessionId, os.getenv('TOKEN_SECRET_SECURE').encode('utf-8'))
    if decoded_data:
        print("Token is valid, data:", decoded_data)
        print(f"Ending the interview with {sessionId}!")
        sh = shelve.open("sessions") 
        del sh[sessionId]
        sh.close()
        return {"endInterview": True}
    else:
        print("Invalid token or corrupted data")
        return {"endInterview": False}
    
# @app.route("/ai/getHelp" , methods=["POST"])
# def getHelp():
#     codeLanguage = request.json['codeLanguage']
#     currentAssesmentDescription = request.json['currentAssesmentDescription']
#     currentCode = request.json['currentCode']
#     count = mockInterviewMain.countTokens(userMessage)
#     print(count.total_tokens)
#     return {"total_tokens": count.total_tokens}


if(__name__) == "__main__":
    app.run(debug=True, port=5001)