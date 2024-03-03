import os

import vertexai
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai import generative_models
from vertexai.generative_models import (ChatSession, Content,
                                        FunctionDeclaration, GenerativeModel,
                                        Part, Tool)

import database_attom
import vectorstore

load_dotenv('.env')

credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
if credentials.expired:
   credentials.refresh(Request())

vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)
PostgresAgentModel = GenerativeModel("gemini-1.0-pro")
AddressParserModel = GenerativeModel("gemini-1.0-pro")
MainAgentModel = GenerativeModel("gemini-1.0-pro")

# chroma_client.delete_collection(name="chat_history")
# chat_history_collection = chroma_client.create_collection(name="chat_history")

# chat = MainAgentModel.start_chat()

def get_chat_response(chat: ChatSession, input: str, conversation_history) -> str:
    print(conversation_history)
  # Generation config
    config = {"max_output_tokens": 2048, "temperature": 0, "top_p": 1, "top_k": 32}

    # Safety config
    safety_config = {
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }

    generated_sql, db_results=queryGenerator(input)
    if db_results == [] and generated_sql == "No Address Found to Query With":
      prompt = f"""
      Most relevant conversation history is: {conversation_history['documents'][0]} as reference of past discussion with this user. Use this to refer to past conversations with the user. The distances: {conversation_history['distances'][0]} shows the similarity to the user query. 
      The {conversation_history['metadatas'][0]} is metadata where each entry has a "message_time" which shows when that message was sent and "source" which is who sent that message. "AI" being from you and "User" being from the user. Use the indexes of the elements to pair them together and make sense of them.
      You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.
      No specific address was found in this user's input. Answer as best you can without being specific on values as you don't have any.

      You may use a little outside knowledge as well if helpful.
      Suggest to the user good and sound investing strategies and cautions about the property. If an int value makes sense to return as a dollar amount, convert that int to US dollars representation.

      If you determine that there is no address present within the input just answer the question as best you can.

      The human input question is: {input}.
      """
    elif db_results == [] and generated_sql == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
      print("here")
      return "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?"
    elif db_results == []:
      prompt = f"""
     Most relevant conversation history is: {conversation_history['documents'][0]} as reference of past discussion with this user. Use this to refer to past conversations with the user. The distances: {conversation_history['distances'][0]} shows the similarity to the user query. 
      The {conversation_history['metadatas'][0]} is metadata where each entry has a "message_time" which shows when that message was sent and "source" which is who sent that message. "AI" being from you and "User" being from the user. Use the indexes of the elements to pair them together and make sense of them.
      You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.
      An address was found within the user input however we do not hold data for that property in our proprietary database.
      Answer as best you can without being specific on values as you don't have any. Mention that we don't hold data for this input

      You may use a little outside knowledge as well if helpful.
      Suggest to the user good and sound investing strategies and cautions about the property. If an int value makes sense to return as a dollar amount, convert that int to US dollars representation.

      If you determine that there is no address present within the input just answer the question as best you can.

      The human input question is: {input}.
      """
    else:
      prompt = f"""
      Most relevant conversation history is: {conversation_history['documents'][0]} as reference of past discussion with this user. Use this to refer to past conversations with the user. The distances: {conversation_history['distances'][0]} shows the similarity to the user query. 
      The {conversation_history['metadatas'][0]} is metadata where each entry has a "message_time" which shows when that message was sent and "source" which is who sent that message. "AI" being from you and "User" being from the user. Use the indexes of the elements to pair them together and make sense of them.
      You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.

      At your disposal, you have numerous tools to decipher what the user wants from an input.

      Here is the generated postgres sql query used to query the database for relevant data: {generated_sql}. Review it carefully to understand the results.
      Here is the data retrieved from the database from that generated query above that relates to the user input: {db_results}. Review it carefully and infer from it to answer the query appropriately and knowledgibly.
      If the generated sql query is "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?" just ignore the database results. If the input requires database results to answer say: "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?"
      If the database results is an empty list just ignore both the query and the database results.
      Else these will provide the information to answer questions about specific properties and addresses that are in the user's input.


      You may use a little outside knowledge as well if helpful.
      Suggest to the user good and sound investing strategies and cautions about the property. If an int value makes sense to return as a dollar amount, convert that int to US dollars representation.

      Summarize your answer and reasonings on the data you get as part of your answer as well! Never show the SQL query though! Only the results.

      If you determine that there is no address present within the input just answer the question as best you can.

      The human input question is: {input}.
      """

    text_response = []
    responses = chat.send_message(prompt, stream=True, generation_config=config, safety_settings=safety_config)
    for chunk in responses:
        text_response.append(chunk.text)
        # print(text_response)
    return "".join(text_response)


def addressFetch(input: str):
  parameters = {
      "max_output_tokens": 1000,
      "temperature": 0,
      "top_p": 1,
      "top_k": 32
  }

  safety_config = {
      generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
      generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
  }

  response = AddressParserModel.generate_content(
      f"""You are a master at parsing and detecting addresses within text. The user input is: {input}. Within this input show me what address or part of an address do you see? If you encounter a state name such as Washington or California.
      Always abbreviate it to its common two letter standard such as WA or CA respectively within the final answer. For zip codes those are 5 letter numbers. For counties only include the name of the county do not add county at the end. Only provide the address or address part that you find within the input and nothing else.
      Format the response to as close to a valid address as possible. Always upper case the whole address you find.
      You can also detect coordinate points if applicable.
      Ignore all other parts of the input.
      If you think there is a possible address within the input but you are unable to give a proper answer say "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?".
      If you think there is no address whatsoever within the input just say "No Address Found"
        """,
          generation_config=parameters,
          safety_settings=safety_config,
  )
#   print(f"Address Parser: {response.text}")
  return response.text


def queryGenerator(input: str):
    config = {"max_output_tokens": 2048, "temperature": 0, "top_p": 1, "top_k": 32}

    # Safety config
    safety_config = {
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }

    # Generate content
    responses = PostgresAgentModel.generate_content(
        [f"""
        You are an agent designed to interact with a postgres SQL database.
        Given an input question, create a syntactically correct postresql query to run that would most accurately return the data needed to, then look at the results of the query and return the answer with the data from the database.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results. But never give more than 30 results! If they want more than 30 return with: "Sorry I cannot provide more than 30 properties at a time"
        You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the given tools. Only use the information returned by the tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        Review the schema here: {database_attom.getTableSchema()}, and know that all tables are connected via the "attom_id" identifier. 
        
        Understand that "table_comment" is not a column in the table but just a comment of what that table is for. Use the "table_comment" to tell you what the table data is used for!
         
        Do Not Make Up Tables! All table names are keys within the schema provided!

        Understand that "amount" holds the actual avm, estimates, or arv values!

        Understand that "location" table does not hold address information. It is purely for coordinate locations and geolocations. The "location" table is where you can find attom_id based on coordinate points.
        Always use "address" table to match anything related to address info such as zip code, counties, cities(locality), street addresses, etc.

        Understand that "column_comment" is not a column in the table but just a simple comment of what that column is for.

        Review the retrieval tool results which are {vectorstore.addressDictSemanticRetreival(input)}. Each main key is a column in the address table with the semantic search results of the address within the user input. Use these values in the query to get the correct attom_id to connect all tables for the query. The distance value is a value of the
        similarity that is available within the database. Always only use results that are below 0.8 in distance as well as prioritize the "one_line" value if the distance is low as that will be the only thing needed to get the attom_id if it is accurate. Never guess "one_line" or "line2" or "line1" if the distance is too high!
        Understand that the "one_line" column contains the full address of a property. Always uppercase the address you are using! If you are not given the attom_id you can search attom_id through the "address" table via the "one_line" column but use the LIKE clause not the =.
        If you are going to use line2 and the distance of line2 in retrieval tool is too high be careful as the zip code may sometimes not match so leave out the zip code and use the LIKE clause.

        If the input is requesting for similar properties around or compared to an address given use the postal1, county, locality, or even the country_subd columns depending on the request but do not make up values that are not more than .5 distance confident from the address retrieval tool above. Do not use the main address but only these components to find comparables!

        If using an alias for result columns use a descriptive name for that column.

        Write an initial draft of the query. Then double check the postgresql query for common mistakes before returning the answer.

        If the question does not seem related to the database, just return "I don't know" as the answer.

        The human input question is: {input}.
        """],
            generation_config=config,
            safety_settings=safety_config,
        )

    # print(responses.text)
    generated_sql = responses.text
    try:
      db_results = database_attom.execute_generated_sql(generated_sql[6:-3])
      # print(f"DB RESULTS: {db_results}")
      return generated_sql, db_results
      # Process or utilize the extracted_query as needed (e.g., for further analysis, but avoid displaying it directly)
    except (ValueError, Exception) as e:
      print("Error from query generator:", e)  # Handle errors appropriately
      return generated_sql, []