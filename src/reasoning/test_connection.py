"""
Phase 7, Step 1: Minimal connectivity test - confirms the API key
and model work BEFORE we build any real reasoning logic on top.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # reads .env into environment variables

client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Reply with exactly one word: 'connected'"}
    ],
    temperature=0,
)

print("Raw response text:", response.choices[0].message.content)
