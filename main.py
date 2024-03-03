from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions

import llm_builds

chroma_client_chat_history = chromadb.PersistentClient(path="~/Downloads/Work")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
chat = llm_builds.MainAgentModel.start_chat()
chat_history_collection = chroma_client_chat_history.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)

def startChat(input, user_id):
    

    chat_history = []

    chat_history = chat_history_collection.query(
            query_texts=[input],
            where={"conversation_user": {"$eq": user_id}},
            n_results=3
        )
    response = llm_builds.get_chat_response(chat, input, chat_history)
    return response