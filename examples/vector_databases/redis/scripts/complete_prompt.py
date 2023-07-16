import openai
from pydantic import BaseModel

# Set the default model
GPT_DEFAULT_MODEL = 'gpt-3.5-turbo'
GPT_DEFAULT_SYSTEM_PROMPT = 'You are an AI model that answers questions.'

def complete_prompt(query: str, system_prompt: str, gpt_model: str, temperature: float):
    # Set the GPT Model based on the input or use the default
    gpt_model = gpt_model or GPT_DEFAULT_MODEL
    
    # Set the system prompt based on the input or use the default
    system_prompt = system_prompt or GPT_DEFAULT_SYSTEM_PROMPT

    response = openai.ChatCompletion.create(
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query},
        ],
        model=GPT_DEFAULT_MODEL #gpt_model,
        temperature=temperature,
    )
    return response['choices'][0]['message']['content']
