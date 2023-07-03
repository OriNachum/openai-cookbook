import redis
import numpy as np
import pandas as pd

def index_documents(client: redis.Redis, prefix: str, documents: pd.DataFrame):
    records = documents.to_dict("records")
    for doc in records:
        key = f"{prefix}:{str(doc['id'])}"

        # create byte vectors for title and content
        title_embedding = np.array(doc["question_vector"], dtype=np.float32).tobytes()
        content_embedding = np.array(doc["answer_vector"], dtype=np.float32).tobytes()

        # replace list of floats with byte vectors
        doc["question_vector"] = title_embedding
        doc["answer_vector"] = content_embedding

        client.hset(key, mapping = doc)

