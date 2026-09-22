"""
Diagnostic: ask Groq's API directly which models are actually
available on this key, instead of trusting a possibly-outdated
model name from docs.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

models = client.models.list()
for m in models.data:
    print(m.id)