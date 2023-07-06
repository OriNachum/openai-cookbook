from redis.commands.search.field import (
    TextField,
    VectorField
)
from redis.commands.search.indexDefinition import (
    IndexDefinition,
    IndexType
)

import sys

def create_redis_search_index(data, redis_client):
    # Constants
    VECTOR_DIM = len(data['question_vector'][0]) # length of the vectors
    VECTOR_NUMBER = len(data)                 # initial number of vectors
    INDEX_NAME = "embeddings-index"           # name of the search index
    PREFIX = "doc"                            # prefix for the document keys
    DISTANCE_METRIC = "COSINE"                # distance metric for the vectors (ex. COSINE, IP, L2)

    # Define RediSearch fields for each of the columns in the dataset
    question = TextField(name="question")
    name = TextField(name="company_name") 
    size = TextField(name="company_size") 
    country = TextField(name="company_country") 
    industry = TextField(name="company_industry") 
    model = TextField(name="model")
    question_embedding = VectorField("question_vector",
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": VECTOR_NUMBER,
        }
    )
    model_embedding = VectorField("model_vector",
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": VECTOR_NUMBER,
        }
    )
    fields = [question, name, size, country, industry, model, question_embedding, model_embedding]

    # Check if index exists
    try:
        redis_client.ft(INDEX_NAME).info()
        index_exists = True
    except:
        index_exists = False

    if index_exists:
        print("Index creation skipped.")
        sys.exit()
        #delete_index = input(f"Index {INDEX_NAME} already exists. Do you want to delete it? (y/n): ")
        # if delete_index.lower() == 'y':
        #redis_client.ft(INDEX_NAME).drop_index()
        #     print(f"Index {INDEX_NAME} deleted.")
        # else:

    # Create RediSearch Index
    redis_client.ft(INDEX_NAME).create_index(
        fields = fields,
        definition = IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
    )
    print("Created index")
