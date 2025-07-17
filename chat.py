import getpass
import os
import requests
import json

# Set your Google API key (you can also directly insert it here)
os.environ["GOOGLE_API_KEY"] = "XXXXXXXXXXXXXXXXXx"  # Replace with your API key

# If the API key isn't set in the environment, prompt for it
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google AI: ")

# Define the endpoint for the Gemini 1.5 Pro model
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={os.environ['GOOGLE_API_KEY']}"

# Define the input text
input_text = "Translate the following from English into Italian: Welcome to Italy, Suresh!"

# Define the request payload
data = {
    "contents": [
        {
            "parts": [{"text": input_text}]
        }
    ]
}

# Set headers for the request
headers = {"Content-Type": "application/json"}

# Make the POST request to the API
response = requests.post(url, headers=headers, json=data)

# Process the response
if response.status_code == 200:
    result = response.json()
    
    # Extract the translated text
    output_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Print only input and output
    print(f"Me: {input_text}")
    print(f"Gemini: {output_text}")
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
