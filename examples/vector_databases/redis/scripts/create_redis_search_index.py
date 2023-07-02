from redis.commands.search.field import (
    TextField,
    VectorField
)
from redis.commands.search.indexDefinition import (
    IndexDefinition,
    IndexType
)

def create_redis_search_index(data, redis_client):
    # Constants
    VECTOR_DIM = len(data['title_vector'][0]) # length of the vectors
    VECTOR_NUMBER = len(data)                 # initial number of vectors
    INDEX_NAME = "embeddings-index"           # name of the search index
    PREFIX = "doc"                            # prefix for the document keys
    DISTANCE_METRIC = "COSINE"                # distance metric for the vectors (ex. COSINE, IP, L2)

    # Define RediSearch fields for each of the columns in the dataset
    title = TextField(name="title")
    url = TextField(name="url")
    text = TextField(name="text")
    title_embedding = VectorField("title_vector",
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": VECTOR_NUMBER,
        }
    )
    text_embedding = VectorField("content_vector",
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": VECTOR_NUMBER,
        }
    )
    fields = [title, url, text, title_embedding, text_embedding]

    return_message = ""
    # Check if index exists
    try:
        redis_client.ft(INDEX_NAME).info()
        return_message = "Index already exists"
    except:
        # Create RediSearch Index
        redis_client.ft(INDEX_NAME).create_index(
            fields = fields,
            definition = IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
        )
        return_message = "Created index"  
    
    return return_message