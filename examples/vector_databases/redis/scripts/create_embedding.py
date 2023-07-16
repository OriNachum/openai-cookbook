import openai

from scripts.complete_prompt import complete_prompt
import time 

def create_embedding(user_query: str, max_retries: int = 3) -> list:
    # Creates embedding vector from user query
    system_prompt = "You are a data scientest master in classifiying fintec related content into relevant items. You will get a part of conversation or FAQ, and you will draw out of it a list of most significent fintech or business related terms. Do not explain any of them - only list them in a comma delimited format"
    gpt_model = "gpt-3.5-turbo" #"gpt-4"
    #manipulated_query = complete_prompt(user_query, system_prompt, gpt_model, 0.05)
    manipulated_query = user_query
    
    for i in range(max_retries):
        try:
            embedded_query = openai.Embedding.create(input=manipulated_query,
                                                    model="text-embedding-ada-002",
                                                    )["data"][0]['embedding']
            return embedded_query
        except Exception as e:
            print(f"Error creating embedding: {e}")
            if i < max_retries - 1:  # i is zero indexed
                time.sleep(1)  # wait for 1 second before trying again
            else:
                raise  # re-raise the last exception if max retries reached
