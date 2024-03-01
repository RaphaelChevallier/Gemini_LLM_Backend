import chromadb
from chromadb.utils import embedding_functions

import database_attom
import llm_builds

chroma_client = chromadb.PersistentClient(path="~/Downloads")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

def createVectorStores():
    one_line, line_two, line_one, county, country_subd, postal_code, locality = database_attom.fetchAddressForVectors()
    chroma_client.reset()
    try:
        one_line_collection = chroma_client.get_collection(name="one_line", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="one_line", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="one_line")
    except:
        print("no one_line exists yet")
    one_line_collection = chroma_client.create_collection(name="one_line", embedding_function=sentence_transformer_ef)

    try:
        line_two_collection = chroma_client.get_collection(name="line_two", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="line_two", embedding_function=sentence_transformer_ef)
    except:
        print("no line_two exists yet")
    line_two_collection = chroma_client.create_collection(name="line_two", embedding_function=sentence_transformer_ef)

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
        line_one_collection = chroma_client.get_collection(name="line_one", embedding_function=sentence_transformer_ef)
        chroma_client.delete_collection(name="line_one", embedding_function=sentence_transformer_ef)
    except:
        print("no line_one exists yet")
    line_one_collection = chroma_client.create_collection(name="line_one", embedding_function=sentence_transformer_ef)

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

    # try:
    #     chat_history_collection = chroma_client.get_collection(name="chat_history")
    #     chroma_client.delete_collection(name="chat_history")
    # except:
    #     print("no chat_history exists yet")
    # chat_history_collection = chroma_client.create_collection(name="chat_history")

    one_line_collection.add(
        documents=[row[0] for row in one_line],
        ids=[str(row[1]) for row in one_line]
    )

    line_two_collection.add(
        documents=[row[0] for row in line_two],
        ids=[str(index) for index in range(0, len(line_two))]
    )

    line_one_collection.add(
        documents=[row[0] for row in line_one],
        ids=[str(index) for index in range(0, len(line_one))]
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
    return one_line_collection, line_two_collection, line_one_collection, county_collection, postal_code_collection, country_subd_collection, locality_collection

def addressDictSemanticRetreival(input):
    one_line_collection = chroma_client.get_collection(name="one_line" , embedding_function=sentence_transformer_ef)

    line_two_collection = chroma_client.get_collection(name="line_two", embedding_function=sentence_transformer_ef)

    county_collection = chroma_client.get_collection(name="county", embedding_function=sentence_transformer_ef)

    postal_code_collection = chroma_client.get_collection(name="postal_code", embedding_function=sentence_transformer_ef)

    line_one_collection = chroma_client.get_collection(name="line_one", embedding_function=sentence_transformer_ef)

    country_subd_collection = chroma_client.get_collection(name="country_subd", embedding_function=sentence_transformer_ef)

    locality_collection = chroma_client.get_collection(name="locality", embedding_function=sentence_transformer_ef)

    # chat_history_collection = chroma_client.get_collection(name="chat_history", embedding_function=sentence_transformer_ef)
    address_find = llm_builds.addressFetch(input)
    if address_find == "No Address Found":
        return "No Address Found to Query With", []
    elif address_find == "I think there is a valid address within your question but can't exactly pinpoint it. Could you specify the address more please?":
        return address_find, []
    else:
        results = one_line_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        results2 = line_one_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        results3 = line_two_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        results4 = postal_code_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        results5 = locality_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        results6 = country_subd_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        results7 = county_collection.query(
            query_texts=[address_find],
            n_results=1
        )

        address_dict_semantic_retrieval = {"one_line": {"distance": results['distances'][0][0], "value": results['documents'][0][0]}, "line1": {"distance": results2['distances'][0][0], "value": results2['documents'][0][0]}, "line2": {"distance": results3['distances'][0][0], "value": results3['documents'][0][0]},
                        "postal1": {"distance": results4['distances'][0][0], "value": results4['documents'][0][0]}, "locality": {"distance": results5['distances'][0][0], "value": results5['documents'][0][0]}, "country_subd": {"distance": results6['distances'][0][0], "value": results6['documents'][0][0]},
                        "county": {"distance": results7['distances'][0][0], "value": results7['documents'][0][0]}}
        # print(address_dict_semantic_retrieval)
        return address_dict_semantic_retrieval

if __name__ == "__main__":
    createVectorStores()
    addressDictSemanticRetreival("Seattle")