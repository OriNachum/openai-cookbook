import numpy as np
import base64
import redis
from redis.commands.search.field import (
    TextField,
    VectorField,
    NumericField,)
from scripts.create_embedding import create_embedding
from scripts.connect_to_redis import get_redis_client

# Function to save the last processed key to a file
def save_last_key(key):
    with open('last_key.txt', 'w') as f:
        f.write(key)

# Function to load the last processed key from a file
def load_last_key():
    try:
        with open('last_key.txt', 'r') as f:
            return f.read().encode('utf-8')
    except FileNotFoundError:
        return None

redis_client = get_redis_client()
redis_client.ping()

# Connect to the Redis database
INDEX_NAME = "embeddings-index"

# # Define the schema for the new index
# new_index.ft(INDEX_NAME).create_index((
#     TextField('question'),
#     NumericField('answer'),
#     VectorField('embedding', 'FLAT', {
#         'TYPE': 'FLOAT32',
#         'DIM': 1024,  # length of the embedding vector
#         'DISTANCE_METRIC': 'COSINE',  # distance metric for the vectors
#     }),
# ))

# Load the last processed key
last_key = load_last_key()


def update_record(redis_client: redis.Redis, questionId: str):
    print('f{key}: {e}')
    try:
        embedding = ''
        questionId_bytes = questionId #questionId.encode('utf-8')
        id = redis_client.hget(questionId, b"id")
        if id is not None:        
            # Get the question and answer fields
            # Get the question and answer fields
            question = redis_client.hget(questionId_bytes, b"question")
            answer = redis_client.hget(questionId_bytes, b"answer")
    
            # Decode the question and answer fields, treating them as empty strings if they are None
            question = question.decode('utf-8') if question else ""
            answer = answer.decode('utf-8') if answer else ""

            # Concatenate the question and answer fields
            combined_text = f"Q: {question} Answer: {answer}"
            print(combined_text)

            # Create an embedding vector for the combined text
            embedding = create_embedding(combined_text)
            print(combined_text)
            
            # Convert the embedding to bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            print(embedding_bytes)

            # Add the embedding to the document
            redis_client.hset(questionId_bytes, b"embedding2", embedding_bytes)
            print(combined_text)

        else:
            print(f"Error processing document {key}: {e} : {len(embedding)} : ")
    except Exception as e:
            print(f"Error processing document {key}: {e} : {len(embedding)} : ")


print("Created new index.")

# Use a cursor to iterate over the keys in the Redis database
for key in redis_client.scan_iter('doc:*'):
    # If a last key is loaded, skip keys until we reach the last key
    if last_key is not None:
        print(last_key)
        if key != last_key:
            print(f"continuing {key}")
            continue
        elif key == last_key:
            print("found it!")
            last_key = None
            continue
    if last_key is not None and key != last_key:
        continue
    elif last_key is not None and key == last_key:
        last_key = None
        continue
    try:
        update_record(redis_client, key)
        # Save the last processed key
        #save_last_key(key)
        print(f"Added document {key} to new index.")
    except Exception as e:
            print(f"Error processing document {key}: {e}")



