import os
from datetime import datetime

import chromadb
import vertexai
from chromadb.utils import embedding_functions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import Content, GenerativeModel, Part

import database_attom
import llm_builds

credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
if credentials.expired:
   credentials.refresh(Request())

vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)

MainAgentModel = GenerativeModel("gemini-1.0-pro")
AddressAgentModel = GenerativeModel("gemini-1.0-pro", tools=[llm_builds.correct_address_input])
PostgresAgentModel = GenerativeModel("gemini-1.0-pro")

def countTokens(input):
    return MainAgentModel.count_tokens(input)

def questionLLMs(input, user_id):

    chroma_client_chat_history = chromadb.PersistentClient(path="~/Downloads/Work")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    chat_history_collection = chroma_client_chat_history.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)
    chat_history_raw_messages = database_attom.getLatestChatHistoryFromUser('f926df36-4fa0-4187-ba9e-d8746d01f601')

    chat = MainAgentModel.start_chat()
    addressChat = AddressAgentModel.start_chat()

    for message in chat_history_raw_messages:
        chat.history.append(Content(role=message['role'], parts=[Part.from_text(message['text'])]))
        addressChat.history.append(Content(role=message['role'], parts=[Part.from_text(message['text'])]))

    relevant_history = chat_history_collection.query(
            query_texts=[input],
            # where={"conversation_user": {"$eq": user_id}},
            n_results=3
        )
    response = llm_builds.get_chat_response(chat, input, MainAgentModel, relevant_history, PostgresAgentModel, addressChat)
    return response