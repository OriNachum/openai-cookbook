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
            return f.read()
    except FileNotFoundError:
        return None

redis_client = get_redis_client()
redis_client.ping()

# Connect to the Redis database
r = redis.Redis(host='localhost', port=6379, db=0)

# Create a new RediSearch client for the old and new indexes
old_index = get_redis_client()
new_index = get_redis_client()

# Define the schema for the new index
new_index.create_index((
    TextField('question'),
    NumericField('answer'),
    VectorField('embedding', 'FLAT', {
        'TYPE': 'FLOAT32',
        'DIM': 1024,  # length of the embedding vector
        'DISTANCE_METRIC': 'COSINE',  # distance metric for the vectors
    }),
))

# Load the last processed key
last_key = load_last_key()

# Use a cursor to iterate over the keys in the Redis database
for key in r.scan_iter('question_vector:*'):
    # If a last key is loaded, skip keys until we reach the last key
    if last_key is not None and key != last_key:
        continue
    elif last_key is not None and key == last_key:
        last_key = None
        continue

    # Get the document from the old index
    doc = old_index.get_document(key)

    # Concatenate the question and answer fields
    combined_text = f"Q: {doc.fields['question']} Answer: {doc.fields['answer']}"

    # Create an embedding vector for the combined text
    embedding = create_embedding(combined_text)

    # Add the document and its embedding to the new index
    new_index.add_document(doc.docid, embedding=embedding, **doc.fields)

    # Save the last processed key
    save_last_key(key)
