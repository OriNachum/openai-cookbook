import openai
from pydantic import BaseModel

# Set the default model
GPT_DEFAULT_MODEL = 'gpt-3.5-turbo'
GPT_DEFAULT_TEMPERATURE = 30
GPT_DEFAULT_SYSTEM_PROMPT = 'You are an AI model that answers questions.'
# Define the model for the request body
class QueryParams(BaseModel):
    systemPrompt: str = None
    gptModel: str = None
    temperature: int = GPT_DEFAULT_TEMPERATURE

def complete_prompt(query: str, params: QueryParams):
    # Set the GPT Model based on the input or use the default
    gpt_model = params.gptModel or GPT_DEFAULT_MODEL

    # Set the temperature on the input or use the default
    gpt_temperature = params.temperature or GPT_DEFAULT_TEMPERATURE
  
    # Set the system prompt based on the input or use the default
    system_prompt = params.systemPrompt or GPT_DEFAULT_SYSTEM_PROMPT

    response = openai.ChatCompletion.create(
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query},
        ],
        model=gpt_model,
        temperature=gpt_temperature,
    )
    return response['choices'][0]['message']['content']
