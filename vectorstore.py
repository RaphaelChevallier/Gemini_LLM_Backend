import os
from datetime import datetime

import chromadb
import requests
from chromadb.utils import embedding_functions
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import Content, GenerativeModel, Part

import database_attom
import llm_builds

chroma_client = chromadb.PersistentClient(path="~/Downloads")
chroma_client_chat_history = chromadb.PersistentClient(path="~/Downloads/Work")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

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

def createChatHistoryStore():
    chroma_client_chat_history.reset()
    try:
        chat_history_collection = chroma_client_chat_history.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)
        chroma_client_chat_history.delete_collection(name="chat_history", embedding_function=sentence_transformer_ef)
    except:
        print("no chat_history exists yet")
    chat_history_collection = chroma_client_chat_history.create_collection(name="chat_history", embedding_function=sentence_transformer_ef)

    ai_message_results, user_message_results = database_attom.getAllMessagesChat()
    for row in ai_message_results:
        formatted_time = row[3].strftime("%A, %B %d, %Y at %I:%M:%S %p")
        chat_history_collection.add(
        documents=[row[2]],
        metadatas=[{'source': 'model', 'message_time': formatted_time, 'conversation_user': row[1]}],
        ids=[row[0]]
    )
    for row in user_message_results:
        formatted_time = row[3].strftime("%A, %B %d, %Y at %I:%M:%S %p")
        chat_history_collection.add(
        documents=row[2],
        metadatas={'source': 'user', 'message_time': formatted_time, 'conversation_user': row[1]},
        ids=row[0]
    )
    results = chat_history_collection.query(
            query_texts=['Hello! How can I help you today?'],
            n_results=1
        )
    print(results)
    
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

# def addressDictSemanticRetreival(input, mainAgent, relevant_history, chat):
#     one_line_collection = chroma_client.get_collection(name="one_line" , embedding_function=sentence_transformer_ef)

#     county_collection = chroma_client.get_collection(name="county", embedding_function=sentence_transformer_ef)

#     postal_code_collection = chroma_client.get_collection(name="postal_code", embedding_function=sentence_transformer_ef)

#     country_subd_collection = chroma_client.get_collection(name="country_subd", embedding_function=sentence_transformer_ef)

#     locality_collection = chroma_client.get_collection(name="locality", embedding_function=sentence_transformer_ef)

#     # chat_history_collection = chroma_client.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)
#     address_find = llm_builds.addressFetch(input, mainAgent, relevant_history, chat)
#     print(address_find)
#     foundValidAddress = True
#     foundAddresses = []
#     coordinatesFound = []
#     if address_find == "No Address Found":
#         return "No Address Found to Query With", input, False, coordinatesFound
#     elif address_find == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
#         return address_find, input, False, coordinatesFound
#     else:
#         resultList = []
#         splitting = address_find.split("\n---\n")
#         newInput = splitting[1]
#         addresses = splitting[0].split("; ")
#         for addressObject in addresses:
#             splitter = addressObject.split(" -- ")
#             address = splitter[0]
#             addressType = splitter[1]
#             results = one_line_collection.query(
#                 query_texts=[address],
#                 n_results=1
#             )

#             results4 = postal_code_collection.query(
#                 query_texts=[address],
#                 n_results=1
#             )

#             results5 = locality_collection.query(
#                 query_texts=[address],
#                 n_results=1
#             )

#             results6 = country_subd_collection.query(
#                 query_texts=[address],
#                 n_results=1
#             )

#             results7 = county_collection.query(
#                 query_texts=[address],
#                 n_results=1
#             )

#             address_dict_semantic_retrieval = {"one_line": {"distance": results['distances'][0][0], "value": results['documents'][0][0]},
#                             "postal1": {"distance": results4['distances'][0][0], "value": results4['documents'][0][0]}, "locality": {"distance": results5['distances'][0][0], "value": results5['documents'][0][0]}, "country_subd": {"distance": results6['distances'][0][0], "value": results6['documents'][0][0]},
#                             "county": {"distance": results7['distances'][0][0], "value": results7['documents'][0][0]}}
#             resultList.append(address_dict_semantic_retrieval)
#             if address_dict_semantic_retrieval['one_line']['distance'] < .04:
#                 foundAddresses.append(address_dict_semantic_retrieval['one_line']['value'])
#                 newInput = newInput.replace("@", address_dict_semantic_retrieval['one_line']['value'], 1)
#                 coordinatesFound.append(None)
#             elif address_dict_semantic_retrieval['locality']['distance'] < .03 and addressType == 'locality':
#                 foundAddresses.append(address_dict_semantic_retrieval['locality']['value'])
#                 newInput = newInput.replace("@", address_dict_semantic_retrieval['locality']['value'], 1)
#                 coordinatesFound.append(None)
#             elif address_dict_semantic_retrieval['postal1']['distance'] < .03 and addressType == 'postalCode':
#                 foundAddresses.append(address_dict_semantic_retrieval['postal1']['value'])
#                 newInput = newInput.replace("@", address_dict_semantic_retrieval['postal1']['value'], 1)
#                 coordinatesFound.append(None)
#             elif address_dict_semantic_retrieval['county']['distance'] < .03 and addressType == 'county':
#                 foundAddresses.append(address_dict_semantic_retrieval['county']['value'])
#                 newInput = newInput.replace("@", address_dict_semantic_retrieval['county']['value'], 1)
#                 coordinatesFound.append(None)
#             elif address_dict_semantic_retrieval['country_subd']['distance'] < .03 and addressType == 'state':
#                 foundAddresses.append(address_dict_semantic_retrieval['country_subd']['value'])
#                 newInput = newInput.replace("@", address_dict_semantic_retrieval['country_subd']['value'], 1)
#                 coordinatesFound.append(None)
#             else:
#                 url = ""
#                 payload = {}
#                 if addressType != 'address':
#                     url = f"https://api.radar.io/v1/search/autocomplete?query={address}&countryCode=US&layers={addressType}"
#                     headers = {
#                     'Authorization': os.getenv('RADAR_PROJECT_PUBLIC_KEY'),
#                     }
#                 else:
#                     url = f"https://api.radar.io/v1/search/autocomplete?query={address}&countryCode=US&expandUnits=true&layers={addressType}"
#                     headers = {
#                     'Authorization': os.getenv('RADAR_PROJECT_PUBLIC_KEY'),
#                     'expandUnits': 'true'
#                     }
#                 try:
#                     response = requests.request("GET", url, headers=headers, data=payload)
#                     if response.json()['addresses']:
#                         address = response.json()['addresses'][0]['formattedAddress'][:-3]
#                         foundAddresses.append(address.upper())
#                         newInput = newInput.replace("@", address.upper(), 1)
#                         coordinatesFound.append(response.json()['addresses'][0]['geometry']['coordinates'])
#                     else:
#                         newInput = newInput.replace("@", address.upper(), 1)
#                         foundAddresses.append(address.upper())
#                         foundValidAddress = False
#                         coordinatesFound.append(None)
#                 except Exception as e:
#                     newInput = newInput.replace("@", address.upper(), 1)
#                     foundAddresses.append(address.upper())
#                     foundValidAddress = False
#                     coordinatesFound.append(None)

#         print("End result")
#         print(newInput)
#         print(resultList)
#         print(foundValidAddress)
#         print(coordinatesFound)
#         return resultList, newInput, foundValidAddress, coordinatesFound, foundAddresses
    

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
        return "No Address Found to Query With", input, False, coordinatesFound
    elif address_find == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
        return address_find, input, False, coordinatesFound
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
                #if not base address and base_address not in components then add current newAddress and reset to add and reset to new one again
                currentAddressComponents[addressComponent[1]] = addressComponent[0]
                newInput =  newInput.replace(addressComponent[0], "@", 1)
            elif addressComponent[1] not in currentAddressComponents and 'base_address' in currentAddressComponents:
                currentAddressComponents[addressComponent[1]] = addressComponent[0]
                newInput =  newInput.replace(addressComponent[0], "", 1)
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
            # results = one_line_collection.query(
            #     query_texts=[address],
            #     n_results=1
            # )

            # results4 = postal_code_collection.query(
            #     query_texts=[address],
            #     n_results=1
            # )

            # results5 = locality_collection.query(
            #     query_texts=[address],
            #     n_results=1
            # )

            # results6 = country_subd_collection.query(
            #     query_texts=[address],
            #     n_results=1
            # )

            # results7 = county_collection.query(
            #     query_texts=[address],
            #     n_results=1
            # )

            # address_dict_semantic_retrieval = {"one_line": {"distance": results['distances'][0][0], "value": results['documents'][0][0]},
            #                 "postal1": {"distance": results4['distances'][0][0], "value": results4['documents'][0][0]}, "locality": {"distance": results5['distances'][0][0], "value": results5['documents'][0][0]}, "country_subd": {"distance": results6['distances'][0][0], "value": results6['documents'][0][0]},
            #                 "county": {"distance": results7['distances'][0][0], "value": results7['documents'][0][0]}}
            # resultList.append(address_dict_semantic_retrieval)
            # if address_dict_semantic_retrieval['one_line']['distance'] < .04:
            #     foundAddresses.append(address_dict_semantic_retrieval['one_line']['value'])
            #     newInput = newInput.replace("@", address_dict_semantic_retrieval['one_line']['value'], 1)
            #     coordinatesFound.append(None)
            # elif address_dict_semantic_retrieval['locality']['distance'] < .03 and addressType == 'locality':
            #     foundAddresses.append(address_dict_semantic_retrieval['locality']['value'])
            #     newInput = newInput.replace("@", address_dict_semantic_retrieval['locality']['value'], 1)
            #     coordinatesFound.append(None)
            # elif address_dict_semantic_retrieval['postal1']['distance'] < .03 and addressType == 'postalCode':
            #     foundAddresses.append(address_dict_semantic_retrieval['postal1']['value'])
            #     newInput = newInput.replace("@", address_dict_semantic_retrieval['postal1']['value'], 1)
            #     coordinatesFound.append(None)
            # elif address_dict_semantic_retrieval['county']['distance'] < .03 and addressType == 'county':
            #     foundAddresses.append(address_dict_semantic_retrieval['county']['value'])
            #     newInput = newInput.replace("@", address_dict_semantic_retrieval['county']['value'], 1)
            #     coordinatesFound.append(None)
            # elif address_dict_semantic_retrieval['country_subd']['distance'] < .03 and addressType == 'state':
            #     foundAddresses.append(address_dict_semantic_retrieval['country_subd']['value'])
            #     newInput = newInput.replace("@", address_dict_semantic_retrieval['country_subd']['value'], 1)
            #     coordinatesFound.append(None)
            # else:
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
                        if '@' in newInput:
                            newInput = newInput.replace('@', response.json()['addresses'][0]['city'].upper(), 1)
                        else:
                            newInput = newInput.replace(address, response.json()['addresses'][0]['city'].upper(), 1)
                    elif addressType == 'county':
                        if '@' in newInput:
                            newInput = newInput.replace('@', response.json()['addresses'][0]['county'][:-7].upper(), 1)
                        else:
                            newInput = newInput.replace(address, response.json()['addresses'][0]['county'][:-7].upper(), 1)
                    elif addressType == 'postalCode':
                        if '@' in newInput:
                            newInput = newInput.replace('@', response.json()['addresses'][0]['postalCode'].upper(), 1)
                        else:
                            newInput = newInput.replace(address, response.json()['addresses'][0]['postalCode'].upper(), 1)
                    elif addressType == 'state':
                        if '@' in newInput:
                            newInput = newInput.replace('@', response.json()['addresses'][0]['stateCode'].upper(), 1)
                        else:
                            newInput = newInput.replace(address, response.json()['addresses'][0]['stateCode'].upper(), 1)
                    coordinatesFound.append(response.json()['addresses'][0]['geometry']['coordinates'])
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
    # createVectorStores()
    # credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
    # if credentials.expired:
    #     credentials.refresh(Request())

    # vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)

    # MainAgentModel = GenerativeModel("gemini-1.0-pro")
    # addressDictSemanticRetreival("Sure the whole address is 201 Galer St unit 104, Seattle, WA 98109", MainAgentModel)