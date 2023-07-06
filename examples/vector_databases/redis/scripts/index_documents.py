import redis
import numpy as np
import pandas as pd
import ast

def index_documents(client: redis.Redis, prefix: str, documents: pd.DataFrame):
    records = documents.to_dict("records")
    for doc in records:
        key = f"{prefix}:{str(doc['id'])}"

        # create byte vectors for title and content
        # question_embedding = np.array(doc["question_vector"], dtype=np.float32).tobytes()
        # answer_embedding = np.array(doc["answer_vector"], dtype=np.float32).tobytes()
        # Convert string representations of list back to list

        question_vector_list = ast.literal_eval(doc["question_vector"])
        answer_vector_list = ast.literal_eval(doc["answer_vector"])

        # create byte vectors for title and content
        question_embedding = np.array(question_vector_list, dtype=np.float32).tobytes()
        answer_embedding = np.array(answer_vector_list, dtype=np.float32).tobytes()

        # replace list of floats with byte vectors
        doc["question_vector"] = question_embedding
        doc["answer_vector"] = answer_embedding

        client.hset(key, mapping = doc)

