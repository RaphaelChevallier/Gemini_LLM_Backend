import os
import shelve
from datetime import datetime

import vertexai
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import Content, GenerativeModel, Part

import mockInterviewLLM

load_dotenv(".env", override=True)

credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
if credentials.expired:
    credentials.refresh(Request())

vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)

MainAgentModel = GenerativeModel("gemini-1.0-pro")

def countTokens(input):
    return MainAgentModel.count_tokens(input)


def getAdvice(currentAssesmentDescription, email, codeLanguage, currentCode, sessionId):
    print("Made it here")
    chat = MainAgentModel.start_chat()
    sh = shelve.open("sessions")
    aiMessages = sh[sessionId]['aiMessage']
    userMessages = sh[sessionId]['userMessage']
    sh.close()
    if aiMessages and userMessages and len(aiMessages) == len(userMessages):
        for index in range(len(aiMessages)):
            chat.history.append(Content(role='user', parts=[Part.from_text(userMessages[index])]))
            chat.history.append(Content(role='model', parts=[Part.from_text(aiMessages[index])]))

    config = {"max_output_tokens": 800, "temperature": 0.2, "top_p": 1, "top_k": 32}
    prompt = [f"""You are an interviewer at a major software company. You are interviewing an individual for a software engineering role and have decided to give him a coding assesment.
              This is current code at the moment: {currentCode}. Review it and guide him towards a solution without revealing the solution."""]
    response = chat.send_message(prompt, generation_config=config)
    sh = shelve.open("sessions")
    tempUser = sh[sessionId]['userMessage']
    tempUser.append(prompt[0])
    tempAi = sh[sessionId]['aiMessage']
    tempAi.append(response.text)
    sh[sessionId] = {'userEmail': email ,'codeAssesment': currentAssesmentDescription, 'currentCode' : currentCode, 'codeLanguage': codeLanguage, 'userMessage': tempUser, 'aiMessage': tempAi}
    sh.close()
    if response.text:
        return response.text
    else:
        return None
    
def startLLMInterview(codeAssesment, user_email, codeLanguage, sessionId):
    chat = MainAgentModel.start_chat()
    config = {"max_output_tokens": 800, "temperature": 0.2, "top_p": 1, "top_k": 32}
    prompt = [f"""You are an interviewer at a major software company. You are interviewing an individual for a software engineering role and have decided to give him a coding assesment.
              You are here to help him work through the problem as well as challenge him a bit and get to understand him a bit better. Here is the coding problem you are presenting him today that you'd like him to solve: {codeAssesment}. This is the coding language he is using so far: {codeLanguage}.
              Start by introducing yourself by using a human name such as Charlie or something of your choosing. Make this seem as a normal interview. Give a brief rundown/summary of the coding assesment and have him get started. They have one hour."""]
    response = chat.send_message(prompt, generation_config=config)
    sh = shelve.open("sessions")
    sh[sessionId] = {'userEmail': user_email, 'startTime': datetime.now() ,'codeAssesment': codeAssesment, 'codeLanguage': codeLanguage, 'aiMessage': [response.text], 'userMessage': [prompt[0]]}
    sh.close()
    if response.text:
        return response.text
    else:
        return None
    # if chat_history_raw_messages:
    #     for message in chat_history_raw_messages:
    #         chat.history.append(Content(role=message['role'], parts=[Part.from_text(message['text'])]))
    
    # try:
    #     response = mockInterviewLLM.get_chat_response(chat, input, chat)
    #     return response
    # except Exception as e:
    #     print(e)
    #     return "There was a problem with the AI. Please try again or contact us."

