import openai

from scripts.complete_prompt import complete_prompt
import time 

def create_embedding(user_query: str, max_retries: int = 3) -> list:
    # Creates embedding vector from user query
    system_prompt = "You are a data scientist master in rephrasing text before running embedding generation for a vectorDB. You will get a part of a conversation or FAQ, and you will rephrase the sentence with weights on the most important parts of it. Make your best to phrase the content to keep the important information in and noise out."
    gpt_model = "gpt-3.5-turbo" #"gpt-4"
    manipulated_query = complete_prompt(user_query, system_prompt, gpt_model, 0.05)
    #manipulated_query = user_query
    
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
