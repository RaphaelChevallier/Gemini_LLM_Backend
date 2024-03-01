import chromadb
from chromadb.utils import embedding_functions

import llm_builds

chroma_client_chat_history = chromadb.PersistentClient(path="~/Downloads/Work")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma_client_chat_history.reset()

chat_history_collection = chroma_client_chat_history.create_collection(name="chat_history", embedding_function=sentence_transformer_ef)

chat = llm_builds.MainAgentModel.start_chat()

conversation_length = 0  # Initialize conversation history
chat_history = []

input = "I am looking at the property at 724 14TH AVE W, KIRKLAND, WA 98033. The list price is $3,300,000. Comparing with comparable homes recently on the market in the same close area and looking at their data points as well as the current list price, is this a strongly flippable home? List the homes you compared this too."
chat_history = chat_history_collection.query(
        query_texts=[input],
        n_results=5
    )
response = llm_builds.get_chat_response(chat, input, chat_history)
print(response)
chat_history_collection.add(
    documents=[input, response],
    ids=[str(conversation_length), str(conversation_length + 1)]
)
conversation_length += 2


# input = "What more can you tell me on the comparable homes you listed in the previous message you sent?"
# chat_history = chat_history_collection.query(
#         query_texts=[input],
#         n_results=5
#     )
# response = llm_builds.get_chat_response(chat, input, chat_history)
# print(response)
# chat_history_collection.add(
#     documents=[input, response],
#     ids=[str(conversation_length), str(conversation_length + 1)]
# )
# conversation_length += 2