import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant who responds in haiku."
        },
        {
            "role": "user",
            "content": "Explain what an LLM is."
        }
    ]   
)
print(response.choices[0].message.content)
print(f"\nUsage: {response.usage}")
