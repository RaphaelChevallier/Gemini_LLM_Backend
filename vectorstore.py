import os
from datetime import datetime

import chromadb
import PyPDF2
import requests
from chromadb.utils import embedding_functions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from langchain.text_splitter import RecursiveCharacterTextSplitter
from vertexai.generative_models import Content, GenerativeModel, Part

import database_attom

chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_MAIN'))
chroma_client_chat_history = chromadb.PersistentClient(path=os.getenv('CHROMA_CLIENT_HISTORY'))
chroma_client_real_estate_strategy = chromadb.PersistentClient(path=os.getenv('CHROMA_STRATEGIES'))
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

def pdf_to_text(file_path):
    pdf_file = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range( len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    pdf_file.close()
    return text

async def updateChatHistoryStore(user_id):
    chat_history_collection = chroma_client_chat_history.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)

    ai_message_results, user_message_results = database_attom.getUpdatedMessagesChat(user_id)
    for row in ai_message_results:
        formatted_time = row[3].strftime("%A, %B %d, %Y at %I:%M:%S %p")
        chat_history_collection.add(
        documents=[row[2]],
        metadatas=[{'source': 'model', 'message_time': formatted_time, 'conversation_user': user_id}],
        ids=[row[0]]
    )
    for row in user_message_results:
        formatted_time = row[3].strftime("%A, %B %d, %Y at %I:%M:%S %p")
        chat_history_collection.add(
        documents=row[2],
        metadatas={'source': 'user', 'message_time': formatted_time, 'conversation_user': user_id},
        ids=row[0]
    )

def createStrategyStore():
    chroma_client_real_estate_strategy.reset()
    try:
        chroma_strategy_collection = chroma_client_real_estate_strategy.get_collection(name="strategy", embedding_function=sentence_transformer_ef)
        chroma_client_real_estate_strategy.delete_collection(name="strategy", embedding_function=sentence_transformer_ef)
    except:
        print("no strategy store exists yet")
    chroma_strategy_collection = chroma_client_real_estate_strategy.create_collection(name="strategy", embedding_function=sentence_transformer_ef)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=150)

    for filename in os.listdir('./public'):
        if filename.endswith('.pdf'):
            print("Starting: " + filename)
            # Convert PDF to text
            text = pdf_to_text(os.path.join('./public', filename))
            # Split text into chunks
            chunks = text_splitter.split_text(text)
            # Convert chunks to vector representations and store in Chroma DB
            documents_list = []
            ids_list = []
            metadatas_list = []
            for i, chunk in enumerate(chunks):

                documents_list.append(chunk)
                metadatas_list.append({"source": filename})
                ids_list.append(f"{filename}_{i}")
            
            chroma_strategy_collection.add(
                documents=documents_list,
                metadatas=metadatas_list,
                ids=ids_list
            )
            print("Ending: " + filename)
    test = chroma_strategy_collection.query(
            query_texts=['What is seller financing?'],
            n_results=10
        )
    print(test)
    print("Finished new strategy embeddings")

def createChatHistoryStore():
    chroma_client_chat_history.reset()
    try:
        chat_history_collection = chroma_client_chat_history.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)
        chroma_client_chat_history.delete_collection(name="chat_history", embedding_function=sentence_transformer_ef)
    except:
        print("no chat_history exists yet")
    chat_history_collection = chroma_client_chat_history.create_collection(name="chat_history", embedding_function=sentence_transformer_ef)

    # ai_message_results, user_message_results = database_attom.getUpdatedMessagesChat()
    # for row in ai_message_results:
    #     formatted_time = row[3].strftime("%A, %B %d, %Y at %I:%M:%S %p")
    #     chat_history_collection.add(
    #     documents=[row[2]],
    #     metadatas=[{'source': 'model', 'message_time': formatted_time, 'conversation_user': row[1]}],
    #     ids=[row[0]]
    # )
    # for row in user_message_results:
    #     formatted_time = row[3].strftime("%A, %B %d, %Y at %I:%M:%S %p")
    #     chat_history_collection.add(
    #     documents=row[2],
    #     metadatas={'source': 'user', 'message_time': formatted_time, 'conversation_user': row[1]},
    #     ids=row[0]
    # )
    # results = chat_history_collection.query(
    #         query_texts=['Hello! How can I help you today?'],
    #         n_results=1
    #     )
    
def createVectorStores():
    one_line, county, country_subd, postal_code, locality = database_attom.fetchAddressForVectors()
    chroma_client.reset()
    try:
        one_line_collection = chroma_client.get_collection(name="one_line", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="one_line", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="one_line")
    except:
        print("no one_line exists yet")
    one_line_collection = chroma_client.create_collection(name="one_line", embedding_function=sentence_transformer_ef)

    try:
        county_collection = chroma_client.get_collection(name="county", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="county", embedding_function=sentence_transformer_ef)
    except:
        print("no county exists yet")
    county_collection = chroma_client.create_collection(name="county", embedding_function=sentence_transformer_ef)

    try:
        postal_code_collection = chroma_client.get_collection(name="postal_code", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="postal_code", embedding_function=sentence_transformer_ef)
    except:
        print("no postal_code exists yet")
    postal_code_collection = chroma_client.create_collection(name="postal_code", embedding_function=sentence_transformer_ef)

    try:
        country_subd_collection = chroma_client.get_collection(name="country_subd", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="country_subd", embedding_function=sentence_transformer_ef)
    except:
        print("no country_subd exists yet")
    country_subd_collection = chroma_client.create_collection(name="country_subd", embedding_function=sentence_transformer_ef)

    try:
        locality_collection = chroma_client.get_collection(name="locality", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="locality", embedding_function=sentence_transformer_ef)
    except:
        print("no locality exists yet")
    locality_collection = chroma_client.create_collection(name="locality", embedding_function=sentence_transformer_ef)

    

    one_line_collection.add(
        documents=[row[0] for row in one_line],
        ids=[str(row[1]) for row in one_line]
    )
    county_collection.add(
        documents=[row[0] for row in county],
        ids=[str(index) for index in range(0, len(county))]
    )

    postal_code_collection.add(
        documents=[row[0] for row in postal_code],
        ids=[str(index) for index in range(0, len(postal_code))]
    )

    country_subd_collection.add(
        documents=[row[0] for row in country_subd],
        ids=[str(index) for index in range(0, len(country_subd))]
    )

    locality_collection.add(
        documents=[row[0] for row in locality],
        ids=[str(index) for index in range(0, len(locality))]
    )

    print("Finished initializing vector stores!")
    return one_line_collection, county_collection, postal_code_collection, country_subd_collection, locality_collection
    

def addressDictSemanticRetreival(input, address_find):
    one_line_collection = chroma_client.get_collection(name="one_line" , embedding_function=sentence_transformer_ef)

    county_collection = chroma_client.get_collection(name="county", embedding_function=sentence_transformer_ef)

    postal_code_collection = chroma_client.get_collection(name="postal_code", embedding_function=sentence_transformer_ef)

    country_subd_collection = chroma_client.get_collection(name="country_subd", embedding_function=sentence_transformer_ef)

    locality_collection = chroma_client.get_collection(name="locality", embedding_function=sentence_transformer_ef)

    newInput = input
    foundValidAddress = True
    foundAddresses = []
    coordinatesFound = []
    newAddressFind = []
    if address_find == "No Address Found":
        return "No Address Found to Query With", input, False, coordinatesFound, foundAddresses
    elif address_find == []:
        return "No Address Found to Query With", input, False, coordinatesFound, foundAddresses
    elif address_find == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
        return address_find, input, False, coordinatesFound, foundAddresses
    else:
        resultList = []
        currentAddressComponents = {}
        print(newInput)
        for addressComponent in address_find:
            if addressComponent[1] in currentAddressComponents and addressComponent[1] == 'base_address':
                # if base_address and no current base address then add
                brandNewAddress = ""
                for values in currentAddressComponents.values():
                    if brandNewAddress != "":
                        brandNewAddress += ", " + values
                    else:
                        brandNewAddress += values
                newInput =  newInput.replace(addressComponent[0], "@", 1)
                newAddressFind.append([brandNewAddress, 'address'])
                currentAddressComponents = {}
                currentAddressComponents[addressComponent[1]] = addressComponent[0]
            elif addressComponent[1] not in currentAddressComponents and 'base_address' not in currentAddressComponents and addressComponent[1] != 'base_address':
                #if not base address and base_address not in components then add current newAddress and reset to add and reset to new one again
                currentAddressComponents = {}
                newAddressFind.append([addressComponent[0], addressComponent[1]])
                newInput =  newInput.replace(addressComponent[0], "@", 1)
            elif addressComponent[1] not in currentAddressComponents and addressComponent[1] == 'base_address':
                #if base address and base_address not in components then add current newAddress and reset to add and reset to new one again
                currentAddressComponents[addressComponent[1]] = addressComponent[0]
                newInput =  newInput.replace(addressComponent[0], "@", 1)
            elif addressComponent[1] not in currentAddressComponents and 'base_address' in currentAddressComponents:
                currentAddressComponents[addressComponent[1]] = addressComponent[0]
                last_a_index = newInput.rfind('@')
                substringToReplace = newInput[last_a_index:last_a_index + len(addressComponent[0]) + 1]
                newInput =  newInput.replace(substringToReplace, "", 1)
                #add and go to next
        if currentAddressComponents:
            brandNewAddress = ""
            for values in currentAddressComponents.values():
                if brandNewAddress != "":
                    brandNewAddress += ", " + values
                else:
                    brandNewAddress += values
            newInput =  newInput.replace(addressComponent[0], "@", 1)
            newAddressFind.append([brandNewAddress, 'address'])
        print(newInput)

        for addressObject in newAddressFind:
            print(addressObject)
            address = addressObject[0]
            addressType = addressObject[1]
            url = ""
            payload = {}
            if addressType != 'address':
                url = f"https://api.radar.io/v1/search/autocomplete?query={address}&countryCode=US&layers={addressType}"
                headers = {
                'Authorization': os.getenv('RADAR_PROJECT_PUBLIC_KEY'),
                }
            else:
                url = f"https://api.radar.io/v1/search/autocomplete?query={address}&countryCode=US&expandUnits=true&layers={addressType}"
                headers = {
                'Authorization': os.getenv('RADAR_PROJECT_PUBLIC_KEY'),
                'expandUnits': 'true'
                }
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.json()['addresses']:
                    if response.json()['addresses'][0]['stateCode'] == "WA":
                        if addressType == 'address':
                            improvedAddress = response.json()['addresses'][0]['formattedAddress'][:-3]
                            foundAddresses.append(improvedAddress.upper())
                            mostAccurateDB = one_line_collection.query(
                                query_texts=[improvedAddress.upper()],
                                n_results=1
                            )
                            if mostAccurateDB['distances'][0][0] < .03:
                                improvedAddress = mostAccurateDB['documents'][0][0]
                            if '@' in newInput:
                                newInput = newInput.replace('@', improvedAddress.upper(), 1)
                            else:
                                newInput = newInput.replace(address, improvedAddress.upper(), 1)

                        elif addressType == 'locality':
                            improvedLocality = response.json()['addresses'][0]['city']
                            mostAccurateDB = locality_collection.query(
                                query_texts=[improvedLocality],
                                n_results=1
                            )
                            if mostAccurateDB['distances'][0][0] < .03:
                                improvedLocality = mostAccurateDB['documents'][0][0]
                            if '@' in newInput:
                                newInput = newInput.replace('@', improvedLocality.upper(), 1)
                            else:
                                newInput = newInput.replace(address, improvedLocality.upper(), 1)

                        elif addressType == 'county':
                            improvedCounty = response.json()['addresses'][0]['county'][:-7]
                            mostAccurateDB = county_collection.query(
                                query_texts=[improvedCounty],
                                n_results=1
                            )
                            if mostAccurateDB['distances'][0][0] < .03:
                                improvedCounty = mostAccurateDB['documents'][0][0]
                            if '@' in newInput:
                                newInput = newInput.replace('@', improvedCounty.upper(), 1)
                            else:
                                newInput = newInput.replace(address, improvedCounty.upper(), 1)

                        elif addressType == 'postalCode':
                            improvedPostalCode = response.json()['addresses'][0]['postalCode']
                            mostAccurateDB = postal_code_collection.query(
                                query_texts=[improvedPostalCode],
                                n_results=1
                            )
                            if mostAccurateDB['distances'][0][0] < .03:
                                improvedPostalCode = mostAccurateDB['documents'][0][0]
                            if '@' in newInput:
                                newInput = newInput.replace('@', improvedPostalCode.upper(), 1)
                            else:
                                newInput = newInput.replace(address, improvedPostalCode.upper(), 1)
                        
                        elif addressType == 'state':
                            improvedState = response.json()['addresses'][0]['stateCode']
                            mostAccurateDB = country_subd_collection.query(
                                query_texts=[improvedState],
                                n_results=1
                            )
                            if mostAccurateDB['distances'][0][0] < .03:
                                improvedState = mostAccurateDB['documents'][0][0]
                            if '@' in newInput:
                                newInput = newInput.replace('@', improvedState.upper(), 1)
                            else:
                                newInput = newInput.replace(address, improvedState.upper(), 1)
                        coordinatesFound.append(response.json()['addresses'][0]['geometry']['coordinates'])
                    else:
                        newInput = newInput.replace(address, address.upper(), 1)
                        foundAddresses.append(address.upper())
                        foundValidAddress = False
                        coordinatesFound.append(None)
                        return "No addresses found in a valid state. Only able to look at Washington addresses.", newInput, foundValidAddress, coordinatesFound, foundAddresses
                else:
                    newInput = newInput.replace(address, address.upper(), 1)
                    foundAddresses.append(address.upper())
                    foundValidAddress = False
                    coordinatesFound.append(None)
            except Exception as e:
                newInput = newInput.replace(address, address.upper(), 1)
                foundAddresses.append(address.upper())
                foundValidAddress = False
                coordinatesFound.append(None)

        print("End result")
        print(newInput)
        print(resultList)
        print(foundValidAddress)
        print(coordinatesFound)
        return resultList, newInput, foundValidAddress, coordinatesFound, foundAddresses
    
if __name__ == "__main__":
    createChatHistoryStore()
    createVectorStores()
    createStrategyStore()