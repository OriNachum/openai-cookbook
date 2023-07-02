from typing import List
import sys
import os
import openai
import nbutils


from scripts.do_validate_key import do_validate_key
from scripts.connect_to_redis import get_redis_client
from scripts.create_redis_search_index import create_redis_search_index
from scripts.load_documents_into_the_index import index_documents

VALIDATE_KEY_RESULT = do_validate_key(openai)
print(VALIDATE_KEY_RESULT)

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

# nbutils.download_wikipedia_data() # already done
data = nbutils.read_wikipedia_data()

# validate results
data.head()

redis_client = get_redis_client()
redis_client.ping()

CREATE_INDEX_RESULT = create_redis_search_index(data, redis_client)
print(CREATE_INDEX_RESULT)

PREFIX = "doc"                            # prefix for the document keys

index_documents(redis_client, PREFIX, data)
print("Loaded {redis_client.info()['db0']['keys']} documents in Redis search index with name: {INDEX_NAME}")


