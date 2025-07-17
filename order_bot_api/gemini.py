import requests
import json
from config import GOOGLE_API_KEY

def ask_gemini(input_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=**********"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": input_text}]}]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        return f"Gemini API Error: {response.status_code} - {response.text}"
