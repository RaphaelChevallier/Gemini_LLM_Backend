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

def get_chat_response(chat: ChatSession, input: str, mainAgent: GenerativeModel, relevant_history, PostgresAgentModel: GenerativeModel, addressChat: ChatSession, relevant_strategy) -> str:
  # Generation config
    config = {"max_output_tokens": 1500, "temperature": 0, "top_p": 1, "top_k": 32}

    # Safety config
    safety_config = {
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    table_schema = database_attom.getTableSchema()

    db_results, newInput, listOfNeighbors, addressesFound = queryGenerator(input, mainAgent, table_schema, relevant_history, PostgresAgentModel, addressChat)
    print(db_results)
    if db_results and db_results != "No Address Found to Query With" and db_results !=  "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?" and db_results != [] and "I detected an address within your query but couldn't find one that is currently in an available state." not in db_results:
        for d in db_results:
            new_dict = {key: value for key, value in d.items() if value is not None}
            if len(new_dict) != 0:
                db_results.append(new_dict)
            db_results.remove(d)
    if db_results == "No Address Found to Query With":
        config = {"max_output_tokens": 500, "temperature": 0.1, "top_p": 1, "top_k": 32}
        prompt = f"""
        You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.
        No specific address was found in this user's input. Answer as best you can without being specific on values as you don't have any.

        Here is a list of past messages you had with this user that may be helpful in answering the user's input: {relevant_history['documents'][0]}. And here's the metadata of those messages respectively: {relevant_history['metadatas'][0]}. The "message_time" in the metadata is the time that message was sent and the "source" in the metadata was who sent that message.
        If you see a past message that answers or helps to answer the current question you can use it as reasoning.

        Here is a list of documents that may relate and answer the user's input: {relevant_strategy['documents'][0]}. These are the respective metadata sources of each exerpt:{relevant_strategy['metadatas'][0]}. Use it at your disgression to inform your insights and reasonings if you find any of it useful to help answer the user.
        Use your some of your own reasoning on the data you have. Think in terms of both the buyer's perspective and the seller's perspective unless asked specifically otherwise.

        Do not use # symbol to format your response!
        Use bulletpoints and headings and other formatting to format your answer and avoid unnecessary jargon and text!

        ---The user input question to answer is: {newInput}---
        """
    elif "I detected an address within your query but couldn't find one that is currently in an available state." in db_results:
        config = {"max_output_tokens": 500, "temperature": 0, "top_p": 1, "top_k": 32}
        prompt = f"""
        You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.
        You did find an address but it just isn't part of an available State for the user. Inform them that you cannot access a property for that state. You only have access to Washington state.

        Here is a list of past messages you had with this user that may be helpful in answering the user's input: {relevant_history['documents'][0]}. And here's the metadata of those messages respectively: {relevant_history['metadatas'][0]}. The "message_time" in the metadata is the time that message was sent and the "source" in the metadata was who sent that message.
        If you see a past message that answers or helps to answer the current question you can use it as reasoning.

        Here is a list of documents that may relate and answer the user's input: {relevant_strategy['documents'][0]}. These are the respective metadata sources of each exerpt:{relevant_strategy['metadatas'][0]}. Use it at your disgression to inform your insights and reasonings if you find any of it useful to help answer the user.
        Use your some of your own reasoning on the data you have. Think in terms of both the buyer's perspective and the seller's perspective unless asked specifically otherwise.

        Do not use # symbol to format your response!
        Use bulletpoints and headings and other formatting to format your answer and avoid unnecessary jargon and text!

        ---The user input question to answer is: {newInput}---
        """
    elif db_results == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
        return "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?"
    elif db_results == []:
        config = {"max_output_tokens": 1048, "temperature": 0.1, "top_p": 1, "top_k": 32}
        prompt = f"""
        You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.
        An address was found within the user input however we do not hold data for that property in our proprietary database.
        Always mention a list of nearby properties. Here is a list of nearby properties from the address you detected that you can suggest to use that might be a better match that is available in our systems: {listOfNeighbors}.
        Answer as best you can without being specific on values as you don't have any. Mention that we don't hold data for this input

        Here is a list of past messages you had with this user that may be helpful in answering the user's input: {relevant_history['documents'][0]}. And here's the metadata of those messages respectively: {relevant_history['metadatas'][0]}. The "message_time" in the metadata is the time that message was sent and the "source" in the metadata was who sent that message.
        If you see a past message that answers or helps to answer the current question you can use it as reasoning.

        Here is a list of documents that may relate and answer the user's input: {relevant_strategy['documents'][0]}. These are the respective metadata sources of each exerpt:{relevant_strategy['metadatas'][0]}. Use it at your disgression to inform your insights and reasonings if you find any of it useful to help answer the user.
        You may use a little outside knowledge as well if helpful. Think in terms of both the buyer's perspective and the seller's perspective unless asked specifically otherwise.
        Suggest to the user good investing strategies as well as your insights and cautions about the property and the data and information you have. Use your some of your own reasoning on the data you have.

        The first thing in your answer if you derived an address from the user input is to show what address you derived which are: {addressesFound}

        Do not use # to format your response!
        Use bulletpoints and headings and other formatting to format your answer and avoid unnecessary jargon!

        ---The user input question to answer is: {newInput}---
        """
    else:
        prompt = f"""
        You are a real estate expert with vast real estate investing knowledge and strategies. You want to be helpful. Your name is EstateMate.

        At your disposal, you have numerous tools to decipher what the user wants from an input.

        Here is the data retrieved from the database from that generated query above that relates to the user input: {db_results}. Review it carefully and infer from it to answer the query appropriately and knowledgibly.
        If the generated sql query is "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?" just ignore the database results. If the input requires database results to answer say: "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?"
        Else these will provide the information to answer questions about specific properties and addresses that are in the user's input. If a user asks for a list of addresses you can provide them from these database results. "one_line" is a whole address that you have available.
        
        Here is a list of past messages you had with this user that may be helpful in answering the user's input: {relevant_history['documents'][0]}. And here's the metadata of those messages respectively: {relevant_history['metadatas'][0]}. The "message_time" in the metadata is the time that message was sent and the "source" in the metadata was who sent that message.
        If you see a past message that answers or helps to answer the current question you can use it as reasoning.

        Here is a list of documents that may relate and answer the user's input: {relevant_strategy['documents'][0]}. These are the respective metadata sources of each excerpt:{relevant_strategy['metadatas'][0]}. Use it at your disgression to inform your insights and reasonings if you find any of it useful to help answer the user.
        You may use a little outside knowledge you already know as well if helpful. Think in terms of both the buyer's perspective and the seller's perspective unless asked specifically otherwise.
        Suggest to the user good investing strategies on the property as well as your insights and cautions about the property and the data and information you have. Use some of your own reasoning on the data you have and extrapolate from it. You may give your own judgement too but always back up with a disclaimer to do their own research if you do.
        
        If an int value makes sense to return as a dollar amount, convert that int to US dollars representation.

        Never show the SQL query though but explain you got it from your own datasources if the answer comes from the results! If your answer does not come from sql query results then divulge your sources.
        You can combine outside sources with the sql query and results as well but prioritze the database sql results!

        The first thing in your answer if you derived an address from the user input is to show what address you derived which are: {addressesFound}
        If you derived an address then here is also a list of neighbors that you can suggest to check out. Dont always suggest this though only when appropriate: {listOfNeighbors}.

        Do not use # to format your response!
        Use bulletpoints and headings and other formatting to format your answer and avoid unnecessary jargon!

        ---The user input question to answer is: {newInput}---
        """

    text_response = []
    try:
        responses = chat.send_message(prompt, stream=True, generation_config=config, safety_settings=safety_config)
        for chunk in responses:
            text_response.append(chunk.text)
            print(text_response)
        return "".join(text_response)
    except Exception as e:
        print(e)
        print("error")
        return "There was a problem with the AI. Please try again or contact us."

def addressFetch(input: str, PostgresAgentModel: GenerativeModel, table_schema, addressChat: ChatSession):
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

    response = addressChat.send_message(
            f"""
            User Input: "{input}".

            Derive all addresses or address components such as (zip codes, cities, counties, states) from the user input or past messages and context.
            Explicitly always use the tool "get_confirmed_available_addresses_from_input_and_update_input"!

            You must fill the parameters of  "address_find" for this tool using the user's input or past messages and context.
            **"address_find" being an array of arrays containing all addresses or names of potential location components (e.g: zip code, state, county, locality) you found within the context of the original user input. Include as an array where:
            - Index 0: The identified address-related information component (string).
            - Index 1: The category of the component (string) - 'base_address', 'postalCode' for zip codes, 'county' for **names** of counties, 'locality' for localities (**names** of cities, towns), or 'state' for **names** states. For states abbreviate to its common two letter standard. **
            """,
            generation_config=parameters,
            safety_settings=safety_config,
    )
    if response.candidates and response.candidates[0].content.parts[0].function_call.name == "get_confirmed_available_addresses_from_input_and_update_input":
        print(response.candidates[0].content.parts[0])
        # Extract the arguments to use in your API call
        try:
            address_find = (
                response.candidates[0].content.parts[0].function_call.args["address_find"]
            )
        except Exception as e:
            address_find = []

        if address_find == []:
            needDb = dbNeeded(input, PostgresAgentModel, table_schema)
            print("needDb1")
            print(needDb)
            if needDb == "True":
                return "Query Anyways", input, False, [], []
        addressDictSemanticRetreival, newInput, foundValidAddress, coordinates, addressesFound  = vectorstore.addressDictSemanticRetreival(input, address_find)
        return addressDictSemanticRetreival, newInput, foundValidAddress, coordinates, addressesFound
    else: 
        if response.text:
            needDb = dbNeeded(input, PostgresAgentModel, table_schema)
            if needDb == "True":
                return "Query Anyways", input, False, [], []
            else:
                return response.text, input, False, [], []
        else:
            needDb = dbNeeded(input, PostgresAgentModel, table_schema)
            if needDb == "True":
                return "Query Anyways", input, False, [], []
            else:
                return "No Address Found to Query With", input, False, [], []

def dbNeeded(newInput: str, PostgresAgentModel: GenerativeModel, table_schema):
    config = {"max_output_tokens": 10, "temperature": 0, "top_p": 1, "top_k": 32}
    safety_config = {
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
    prompt=[f"""
    You are an expert that knows when a question needs postgres database data to answer the question. Here is your postgres database schema:{table_schema}. Review it carefully!
    Review the schema, and know that all tables are connected via the "attom_id" identifier. 
            
    Understand that "table_comment" is not a column in the table but just a comment of what that table is for. Use the "table_comment" to tell you what the table data is used for!
    
    Do Not Make Up Tables! All table names are keys within the schema provided!

    Understand that "amount" holds the actual avm, estimates, or arv values!

    Understand that "location" table does not hold address information. It is purely for coordinate locations and geolocations. The "location" table is where you can find attom_id based on coordinate points.
    Always use "address" table to match anything related to address info such as zip code, counties, cities(locality), street addresses, etc.

    Understand that "column_comment" is not a column in the table but just a simple comment of what that column is for.

    You're only job is to tell me if the data in the database using that schema can still be used to answer the user input. 
    ---The user input question to answer is: {newInput}---
    Only ever respond with either "True" if the database can help answer the user or "False" if the question does not need the database data to answer with. No other words but "True" or "False"
    """]
    responses = PostgresAgentModel.generate_content(prompt,
                generation_config=config,
                safety_settings=safety_config,
            )
    return responses.text

def queryGenerator(input: str, mainAgent: GenerativeModel, table_schema, relevant_history, PostgresAgentModel: GenerativeModel, addressChat: ChatSession):
    config = {"max_output_tokens": 2048, "temperature": 0, "top_p": 1, "top_k": 32}

    # Safety config
    safety_config = {
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }
    addressDictSemanticRetreival, newInput, foundValidAddress, coordinates, addressesFound  = addressFetch(input, PostgresAgentModel, table_schema, addressChat)
    if addressDictSemanticRetreival == "No Address Found to Query With":
        results = "No Address Found to Query With"
        return results, newInput, coordinates, addressesFound
    if addressDictSemanticRetreival == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
        results = "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?"
        return results, newInput, coordinates, addressesFound
    if "No addresses found in a valid state." in addressDictSemanticRetreival:
        results = "I detected an address within your query but couldn't find one that is currently in an available state."
        return results, newInput, coordinates, addressesFound
    prefix = f"""
            You are an agent designed to interact with a postgres SQL database.
            Given an input question, create a syntactically correct postresql query to run that would most accurately return the data needed to, then look at the results of the query and return the answer with the data from the database.
            Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results. But never give more than 30 results! If they want more than 30 return with: "Sorry I cannot provide more than 30 properties at a time"
            You can order the results by a relevant column to return the most interesting examples in the database.
            Never query for all the columns from a specific table, only ask for the relevant columns given the question.
            You have access to tools for interacting with the database.
            Only use the given tools. Only use the information returned by the tools to construct your final answer.
            You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

            Write an initial draft of the query. Then double check the postgresql query for common mistakes, including:
            - Using NOT IN with NULL values
            - Using UNION when UNION ALL should have been used
            - Using BETWEEN for exclusive ranges
            - Data type mismatch in predicates
            - Properly quoting identifiers
            - Using the correct number of arguments for functions
            - Using the proper columns for joins

            Favor using LIKE rather than = in the query. And favor checking the "one_line" column over "line1" or "line2" to match conditionals.

            Review the schema here: {table_schema}, and know that all tables are connected via the "attom_id" identifier. 
            
            Understand that "table_comment" is not a column in the table but just a comment of what that table is for. Use the "table_comment" to tell you what the table data is used for!
            
            Do Not Make Up Tables! All table names are keys within the schema provided!

            Understand that "amount" holds the actual avm, estimates, or arv values!

            Understand that "location" table does not hold address information. It is purely for coordinate locations and geolocations. The "location" table is where you can find attom_id based on coordinate points.
            Always use "address" table to match anything related to address info such as zip code, counties, cities(locality), street addresses, etc.

            Understand that "column_comment" is not a column in the table but just a simple comment of what that column is for.
        """
    suffix = f"""
            If using an alias for result columns use a descriptive name for that column.

            Write an initial draft of the query. Then double check the postgresql query for common mistakes before returning the answer.
            It is better to grab more data columns using the specified existing columns with the sql command to better answer the user's query and provide more context as well.

            If the question does not seem related to the database, just return "I don't know" as the answer.

            ---The user input question to answer is: {newInput}---
    """
    if foundValidAddress == True:
        main = f"""
            If the input is requesting for similar properties around or compared to an address given use the {addressDictSemanticRetreival} list of similar properties and only use the "postal1", "county", "country_subd", or "locality" keys depending on the request but do not make up values. Do not use the main address but only these components to find comparables in the area!
            """
        prompt = [prefix, main, suffix]
    elif foundValidAddress == False:
        main = f"""
            If the input is requesting for similar properties around or compared to an address given use the postal1, county, locality, or even the country_subd columns depending on the request but do not make up values that are not more than .5 distance confident from the address retrieval tool above. Do not use the main address but only these components to find comparables!
            """
        prompt = [prefix, main, suffix]
    responses = PostgresAgentModel.generate_content(prompt,
            generation_config=config,
            safety_settings=safety_config,
        )
    generated_sql = responses.text
    try:
      listOfNeighbors = []
      db_results = database_attom.execute_generated_sql(generated_sql[6:-3])
      if coordinates != []:
        listOfNeighbors = database_attom.coordinateClosenessSearch(coordinates)

      return db_results, newInput, listOfNeighbors, addressesFound
      # Process or utilize the extracted_query as needed (e.g., for further analysis, but avoid displaying it directly)
    except (ValueError, Exception) as e:
      print("Error from query generator:", e)  # Handle errors appropriately
      return "No Address Found to Query With"

 # Specify a function declaration and parameters for an API request
get_confirmed_available_addresses = FunctionDeclaration(
    name="get_confirmed_available_addresses_from_input_and_update_input",
    description="This will take the user input as well as the addresses you think you found within the original input. Address can be a full address or even a potential location component like zip code, state, county, or locality. It will then update the original input with the confirmed addresses or it will return coordinates of nearest addresses if available",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {#"newInput": {"type": "string", "description": "The original user's input with identified address-related information replaced by placeholders (`@` symbols) for subsequent processing and return. This modified input acts as a template for potential address confirmation or coordinate retrieval."},
                       "address_find": {"type": "array", "description": "Array of arrays containing all addresses or names of potential location components (e.g: zip code, state, county, locality) you found within the context of original user input. Include as an array where: \n" +
  "- Index 0: The identified address-related information component (string). Keep the original case of the string. \n" +
  "- Index 1: The category of the component (string) - 'base_address', 'postalCode' for zip codes, 'county' for **names** of counties, 'locality' for localities (**names** of cities, towns), or 'state' for **names** states. For states abbreviate to its common two letter standard."},
                       }
    },
)

correct_address_input = Tool(
        function_declarations=[
            get_confirmed_available_addresses,
        ],
    )