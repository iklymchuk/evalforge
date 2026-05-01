import os
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()
client = Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system="You are a helpful assistant who responds in haiku.",
    messages=[
        {
            "role": "user",
            "content": "Explain what an LLM is."
        }
    ]
)
print(response.content[0].text)
print(f"\nUsage: {response.usage}")
    