import time

from pinecone import Pinecone, ServerlessSpec, QueryResponse

from komodo.shared.embeddings.openai import get_embeddings
from komodo.shared.utils.lambda_utils import lambda_fetch_secret

pinecone_api_key = lambda_fetch_secret("PINECONE_SERVERLESS_API_KEY")


def describe_pinecone_index(name):
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(name)
    print(index.describe_index_stats())


CACHED_INDICES = {}


def get_pinecone_index(name):
    if name in CACHED_INDICES:
        return CACHED_INDICES[name]

    pc = Pinecone(api_key=pinecone_api_key)
    existing_indexes = [
        index_info["name"] for index_info in pc.list_indexes()
    ]

    # check if index already exists (it shouldn't if this is first time)
    if name not in existing_indexes:
        pc.create_index(
            name,
            dimension=1536,  # dimensionality of minilm
            metric='cosine',  # dotproduct, euclidean, cosine
            spec=ServerlessSpec(
                cloud="aws",
                region="us-west-2"
            )
        )
        # wait for index to be initialized
        while not pc.describe_index(name).status['ready']:
            time.sleep(1)

    # connect to index
    index = pc.Index(name)
    CACHED_INDICES[name] = index
    return index


def delete_pinecone_index(name):
    pc = Pinecone(api_key=pinecone_api_key)
    existing_indexes = [
        index_info["name"] for index_info in pc.list_indexes()
    ]

    # check if index already exists (it shouldn't if this is first time)
    if name in existing_indexes:
        pc.delete_index(name)
        print("Deleted index: " + name)
    else:
        print("Index does not exist: " + name)


def semantic_search(index, query=None, filter=None, namespace=None, k=10) -> QueryResponse:
    args = {}
    args["top_k"] = k
    args["include_values"] = False
    args["include_metadata"] = True

    if query:
        args["vector"] = get_embeddings().embed_query(query)

    if filter:
        args["filter"] = filter

    if namespace:
        args["namespace"] = namespace

    result = index.query(**args)
    return result


def weighted_combine_results(results, weights):
    combined_scores = {}
    for section, ids in results.items():
        weight = weights.get(section, 1)
        for id_ in ids:
            combined_scores[id_] = combined_scores.get(id_, 0) + weight

    # Sort by combined score
    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    return [id_ for id_, score in sorted_results]
