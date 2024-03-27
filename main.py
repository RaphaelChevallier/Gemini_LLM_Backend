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

    
    chroma_client_chat_history = chromadb.PersistentClient(path=os.getenv('CHROMA_CLIENT_HISTORY'))
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    chroma_client_real_estate_strategy = chromadb.PersistentClient(path=os.getenv('CHROMA_STRATEGIES'))
    chat_history_collection = chroma_client_chat_history.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)
    chroma_strategy_collection = chroma_client_real_estate_strategy.get_collection(name="strategy", embedding_function=sentence_transformer_ef)
    
    chat_history_raw_messages = database_attom.getLatestChatHistoryFromUser(user_id)

    chat = MainAgentModel.start_chat(response_validation=False)
    addressChat = AddressAgentModel.start_chat(response_validation=False)

    if chat_history_raw_messages:
        for message in chat_history_raw_messages:
            chat.history.append(Content(role=message['role'], parts=[Part.from_text(message['text'])]))
            addressChat.history.append(Content(role=message['role'], parts=[Part.from_text(message['text'])]))

    relevant_strategy = chroma_strategy_collection.query(
            query_texts=[input],
            n_results=5
        )

    relevant_history = chat_history_collection.query(
            query_texts=[input],
            where={"conversation_user": {"$eq": user_id}},
            n_results=3
        )
    
    try:
        response = llm_builds.get_chat_response(chat, input, MainAgentModel, relevant_history, PostgresAgentModel, addressChat, relevant_strategy)
        return response
    except Exception as e:
        print(e)
        return "There was a problem with the AI. Please try again or contact us."

