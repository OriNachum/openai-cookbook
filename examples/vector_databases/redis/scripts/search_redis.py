import redis
import openai
import numpy as np

from typing import List
from redis.commands.search.query import Query

from scripts.create_embedding import create_embedding


# For using OpenAI to generate query embedding
# results = search_redis(redis_client, 'modern art in Europe', k=10)
# Wikipedia usage examples below

def search_redis(
    redis_client: redis.Redis,
    user_query: str,
    index_name: str = "embeddings-index",
    vector_field: str = "system_index",
    #vector_field: str = "question_vector",
    return_fields: list = ["question", "answer", "date", "quality","qualityreason", "vector_score"],
    hybrid_fields = "*",
    k: int = 20,
    print_results: bool = True,
) -> List[dict]:

    # Creates embedding vector from user query
    embedded_query = create_embedding(user_query)

    # Prepare the Query
    base_query = f'{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]'
    query = (
        Query(base_query)
         .return_fields(*return_fields)
         .sort_by("vector_score")
         .paging(0, k)
         .dialect(2)
    )
    params_dict = {"vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}

    # perform vector search
    results = redis_client.ft(index_name).search(query, params_dict)
    # if print_results:
    #     for i, article in enumerate(results.docs):
    #         score = 1 - float(article.vector_score)
    #         print(f"{i}. {article.question} (Score: {round(score ,3) })")

    # calculate the score for each result and store it in the result
    for result in results.docs:
        result['score'] = calculate_best_score(result['upvotes'], result['downvotes'])

    # sort the results by the calculated score
    results.docs.sort(key=lambda x: x['score'], reverse=True)

    # if print_results:
    #     for i, article in enumerate(results.docs):
    #         score = 1 - float(article.vector_score)
    #         print(f"{i}. {article.question} (Score: {round(score ,3) })")
    return results.docs

# Vector search 
# =============
# results = search_redis(redis_client, 'modern art in Europe', k=10)
# 0. Museum of Modern Art (Score: 0.875)
# 1. Western Europe (Score: 0.868)
# 2. Renaissance art (Score: 0.864)
# 3. Pop art (Score: 0.86)
# 4. Northern Europe (Score: 0.855)
# 5. Hellenistic art (Score: 0.853)
# 6. Modernist literature (Score: 0.847)
# 7. Art film (Score: 0.843)
# 8. Central Europe (Score: 0.843)
# 9. European (Score: 0.841)

# results = search_redis(redis_client, 'Famous battles in Scottish history', vector_field='answer_vector', k=10)
# 0. Battle of Bannockburn (Score: 0.869)
# 1. Wars of Scottish Independence (Score: 0.861)
# 2. 1651 (Score: 0.853)
# 3. First War of Scottish Independence (Score: 0.85)
# 4. Robert I of Scotland (Score: 0.846)
# 5. 841 (Score: 0.844)
# 6. 1716 (Score: 0.844)
# 7. 1314 (Score: 0.837)
# 8. 1263 (Score: 0.836)
# 9. William Wallace (Score: 0.835)

# Hybrid search
# =============
# def create_hybrid_field(field_name: str, value: str) -> str:
#     return f'@{field_name}:"{value}"'

# # search the content vector for articles about famous battles in Scottish history and only include results with Scottish in the title
# results = search_redis(redis_client,
#                        "Famous battles in Scottish history",
#                        vector_field="question_vector",
#                        k=5,
#                        hybrid_fields=create_hybrid_field("embeddingType", "External")
#                        )
