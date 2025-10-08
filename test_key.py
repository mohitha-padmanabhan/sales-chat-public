import os, openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    openai.models.list()          # cheapest possible call
    print("✅ Key is valid & active")
except openai.AuthenticationError:
    print("❌ Invalid key or typo")
except openai.RateLimitError:
    print("⚠️  Key valid but no credits left")