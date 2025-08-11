import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Clé OpenAI standard
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",   # ou "gpt-4o", "gpt-4"
        messages=[
            {"role": "system", "content": "You are an orc."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message['content'].strip()

prompt = "What is the capital of France?"
print(get_response(prompt))
