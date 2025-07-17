import os
import getpass
import google.auth
from google.cloud import generativelanguage_v1beta3 as gen_ai

# Set your Google API key (you can also directly insert it here)
os.environ["GOOGLE_API_KEY"] = "XXXXXXXXXXXXXXXXXx"  # Replace with your API key

# If the API key isn't set in the environment, prompt for it
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google AI: ")

# Initialize the client for Google Generative AI
client = gen_ai.GenerativeLanguageServiceClient()

# Define the model to be used
model = "gemini-2.5-pro-exp-03-25"

# Define the message to be processed
data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Translate the following from English into Italian: Welcome to Italy, Suresh!"
                }
            ]
        }
    ]
}

# Define the config for generating content
generate_content_config = gen_ai.GenerateContentConfig(
    response_mime_type="text/plain",
)

# Prepare the request
request = gen_ai.GenerateContentRequest(
    model=model,
    contents=data['contents'],
    config=generate_content_config,
)

# Call the API to generate content and print results
response = client.generate_content(request=request)

# Output the result
for chunk in response:
    print(chunk.text, end="")

