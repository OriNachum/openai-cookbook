import openai

from scripts.complete_prompt import complete_prompt

def create_embedding(user_query: str) -> list:
    # Creates embedding vector from user query
    system_prompt = "You are a data scientest master in classifiying fintec related content into relevant items. You will get a part of conversation or FAQ, and you will draw out of it a list of most significent fintech or business related terms. Do not explain any of them - only list them in a comma delimited format"
    gpt_model = "gpt-4"
    manipulated_query = complete_prompt(user_query, system_prompt, gpt_model, 0.05)
    
    embedded_query = openai.Embedding.create(input=manipulated_query,
                                            model="text-embedding-ada-002",
                                            )["data"][0]['embedding']
    return embedded_query