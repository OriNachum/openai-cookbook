import redis
import json
import logging

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

logging.basicConfig(level=logging.INFO)

def hash_record(record: NewRecord) -> str:
    record_dict = record.dict()  # Convert the record to a dict
    record_json = json.dumps(record_dict, sort_keys=True)  # Convert the dict to a JSON string
    record_hash = hashlib.sha256(record_json.encode()).hexdigest()  # Hash the JSON string
    return record_hash

def add_records(redis_client: redis.Redis, records: List[NewRecord]):
    new_records = []
    for record in records:
        record_hash = hash_record(record)
        if not redis_client.exists(record_hash):
            new_records.append(record)
            redis_client.set(record_hash, json.dumps(record.dict()))

    if not new_records:
        print("No new records to add.")
        return

    tempfilePath = "/home/ec2-user/git/openai-cookbook/temp.csv"
    with open(tempfilePath, 'w') as file:
        pass

    convert_newrecordlist_to_csv(new_records, tempfilePath)
    add_embeddings_to_csv(tempfilePath)

    # Generate embeddings for each record
    PREFIX = "doc"  # prefix for the document keys
    data = nbutils.read_wikipedia_data("/home/ec2-user/git/openai-cookbook/", "temp")

    index_documents(redis_client, PREFIX, data)
