import openai
from pydantic import BaseModel

# Set the default model
GPT_DEFAULT_MODEL = 'gpt-3.5-turbo'
GPT_DEFAULT_SYSTEM_PROMPT = 'You are an AI model that answers questions.'

def num_tokens_in_string(string: str, model_name: str = "gpt-3.5-turbo") -> int:
    """Returns the number of tokens in a text string for a specific model."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def complete_prompt(query: str, system_prompt: str, gpt_model: str, temperature: float):
    # Set the GPT Model based on the input or use the default
    gpt_model = gpt_model or GPT_DEFAULT_MODEL
    
    # Set the system prompt based on the input or use the default
    system_prompt = system_prompt or GPT_DEFAULT_SYSTEM_PROMPT

    # Estimate the total number of tokens
    num_tokens = num_tokens_in_string(query) + num_tokens_in_string(system_prompt)
    if num_tokens > 2096 and gpt_model == GPT_DEFAULT_MODEL:
        gpt_model = 'gpt-3.5-turbo-16k'

    response = openai.ChatCompletion.create(
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query},
        ],
        model=gpt_model,
        temperature=temperature,
    )
    return response['choices'][0]['message']['content']
