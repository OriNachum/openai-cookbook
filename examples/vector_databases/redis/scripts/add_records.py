import redis

from create_embedding import create_embedding
from typing import List

def get_next_vector_id(redis_client: redis.Redis) -> int:
    vector_id_key = "vector_id_counter"
    vector_id = redis_client.get(vector_id_key)
    if vector_id is None:
        vector_id = 1
        redis_client.set(vector_id_key, vector_id)
    else:
        vector_id = int(vector_id) + 1
        redis_client.set(vector_id_key, vector_id)
    return vector_id


def add_records(redis_client: redis.Redis, records: List[dict]):
    # Generate embeddings for each record
    for record in records:
        question_vector = create_embedding(record["question"])
        answer_vector = create_embedding(record["answer"])

        # Update the record with embeddings and vector_id
        record["question_vector"] = question_vector
        record["answer_vector"] = answer_vector
        record["vector_id"] = get_next_vector_id(redis_client)

    # Add the records to Redis in a pipeline for efficient bulk insert
    pipeline = redis_client.pipeline()
    for record in records:
        pipeline.hset("records", record["question"], str(record))
    pipeline.execute()
