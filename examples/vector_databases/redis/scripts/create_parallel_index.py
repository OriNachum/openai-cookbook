import redis
from redis.commands.search.field import (
    TextField,
    VectorField,
    NumericField,)
from scripts.create_embedding import create_embedding
from scripts.connect_to_redis import get_redis_client


redis_client = get_redis_client()
redis_client.ping()

# Connect to the Redis database
r = redis.Redis(host='localhost', port=6379, db=0)

# Create a new RediSearch client for the old and new indexes
old_index = redis_client('old_index', conn=r)
new_index = redis_client('new_index', conn=r)

# Define the schema for the new index
new_index.create_index((
    TextField('question'),
    NumericField('answer'),
    VectorField('embedding', 'FLAT', {
        'TYPE': 'FLOAT32',
        'DIM': len(1024),  # length of the embedding vector
        'DISTANCE_METRIC': 'COSINE',  # distance metric for the vectors
    }),
))

# Use a cursor to iterate over the keys in the Redis database
for key in r.scan_iter('old_index:*'):
    # Get the document from the old index
    doc = old_index.get_document(key)

    # Concatenate the question and answer fields
    combined_text = f"Q: {doc.fields['question']} Answer: {doc.fields['answer']}"

    # Create an embedding vector for the combined text
    embedding = create_embedding(combined_text)

    # Add the document and its embedding to the new index
    new_index.add_document(doc.docid, embedding=embedding, **doc.fields)
