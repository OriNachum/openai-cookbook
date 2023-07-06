import redis
from datetime import date
from scripts.add_embeddings_to_csv import add_embeddings_to_csv
from scripts.convert_newrecordlist_to_csv import convert_newrecordlist_to_csv
from scripts.index_documents import index_documents
import pandas as pd

from scripts.create_embedding import create_embedding
from typing import List
from pydantic import BaseModel

import scripts.nbutils as nbutils


# Define Pydantic models
class NewRecord(BaseModel):
    question: str
    question_vector: str
    answer: str
    answer_vector: str
    vector_id: int
    isWin: bool
    companyName: str
    companySize: str
    companyCountry: str
    companyIndustry: str
    conversationDate: date



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
    tempfilePath="/home/ec2-user/git/openai-cookbook/temp.csv"
    convert_newrecordlist_to_csv(records, tempfilePath)
    add_embeddings_to_csv(tempfilePath)
    # Generate embeddings for each record
    PREFIX = "doc"  # prefix for the document keys
    data = nbutils.read_wikipedia_data("/home/ec2-user/git/openai-cookbook/","temp")

    index_documents(redis_client, PREFIX, data)
