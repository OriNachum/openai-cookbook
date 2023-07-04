import openai

def create_embedding(user_query: str) -> list:
    # Creates embedding vector from user query
    embedded_query = openai.Embedding.create(input=user_query,
                                            model="text-embedding-ada-002",
                                            )["data"][0]['embedding']
    return embedded_query