import os
import shelve
from datetime import datetime

import vertexai
from chromadb.utils import embedding_functions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import GenerativeModel

import mockInterviewLLM

credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
if credentials.expired:
   credentials.refresh(Request())

vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)

MainAgentModel = GenerativeModel("gemini-1.0-pro")

def countTokens(input):
    return MainAgentModel.count_tokens(input)

def startLLMInterview(codeAssesment, user_email, codeLanguage, sessionId):
    
    # chat_history_raw_messages = database_attom.getLatestChatHistoryFromUser(user_id)

    chat = MainAgentModel.start_chat()

    sh = shelve.open("sessions")
    sh[sessionId] = {'userEmail': user_email, 'startTime': datetime.now() ,'codeAssesment': codeAssesment, 'codeLanguage': codeLanguage, 'aiChat': chat}
    sh.close()
    print("done")
    # if chat_history_raw_messages:
    #     for message in chat_history_raw_messages:
    #         chat.history.append(Content(role=message['role'], parts=[Part.from_text(message['text'])]))
    return
    # try:
    #     response = mockInterviewLLM.get_chat_response(chat, input, chat)
    #     return response
    # except Exception as e:
    #     print(e)
    #     return "There was a problem with the AI. Please try again or contact us."

