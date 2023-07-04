import redis
from datetime import date
from scripts.index_documents import index_documents
import pandas as pd

from scripts.create_embedding import create_embedding
from typing import List
from pydantic import BaseModel

# Define Pydantic models
class NewRecord(BaseModel):
    question: str
    answer: str
    question_vector: str
    answer_vector: str
    vector_id: int
    date: date
    company_name: str
    company_size: str
    company_location: str
    company_industry: str


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


def add_records(redis_client: redis.Redis, records: List[NewRecord]):
    # Generate embeddings for each record
    PREFIX = "doc"  # prefix for the document keys

    records_df = pd.DataFrame(records)
    for record in records_df.iterrows():
        question = record["question"]
        answer = record["answer"]
        question_vector = create_embedding(question)
        answer_vector = create_embedding(answer)

        record["question_vector"] = question_vector
        record["answer_vector"] = answer_vector
        record["vector_id"] = get_next_vector_id(redis_client)


    index_documents(redis_client, PREFIX, records_df)
