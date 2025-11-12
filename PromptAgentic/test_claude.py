"""
Simple test script to verify Claude API is working
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Test API call
print("Testing Claude API connection...")
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=50,
    messages=[{"role": "user", "content": "Say 'Hello, I am Claude!' in exactly 5 words."}]
)

print("Response:", response.content[0].text)
print("\nSuccess! Claude API is working correctly.")
