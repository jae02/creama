# Quick test: is Gemini API available right now?
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

try:
    resp = model.generate_content("Say hello in Korean, one word only.")
    print(f"[OK] Gemini works! Response: {resp.text.strip()}")
except Exception as e:
    print(f"[FAIL] {e}")
