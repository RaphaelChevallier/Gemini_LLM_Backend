import os
import shelve
from datetime import datetime

import vertexai
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import GenerativeModel

import mockInterviewLLM

load_dotenv(".env", override=True)

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
    config = {"max_output_tokens": 800, "temperature": 0.2, "top_p": 1, "top_k": 32}
    prompt = [f"""You are an interview at a major software company. You are interviewing an individual for a software engineering role and have decided to give him a coding assesment.
              You are here to help him work through the problem as well as challenge him a bit and get to understand him a bit better. Here is the coding problem you are presenting him today that you'd like him to solve: {codeAssesment}. This is the coding language he is using so far: {codeLanguage}.
              Start by introducing yourself by using a human name such as Charlie or something of your choosing. Make this seem as a normal interview. Give a brief rundown of the coding assesment and have him get started. He has one hour."""]
    response = chat.send_message(prompt, generation_config=config)
    print(response)
    sh = shelve.open("sessions")
    sh[sessionId] = {'userEmail': user_email, 'startTime': datetime.now() ,'codeAssesment': codeAssesment, 'codeLanguage': codeLanguage}
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

