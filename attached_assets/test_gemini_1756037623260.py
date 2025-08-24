import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("🔑 Gemini API Key loaded:", bool(api_key))

if not api_key:
    print("❌ API key is missing. Check your .env file and variable name.")
    exit()

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Test message
test_prompt = "Give a short summary of common cold symptoms."
try:
    response = model.generate_content(test_prompt)
    print("✅ AI Response:", response.text)
except Exception as e:
    print("❌ Error:", e)
