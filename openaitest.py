import os
import openai
from config import apikey  # Ensure your API key is correctly stored and imported

# Set the API key from your config file
openai.api_key = apikey

try:
    # Create a chat completion request
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model to use
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write an email to my boss for resignation."}
        ],
        temperature=0.7,  # Adjust temperature for randomness in response
        max_tokens=256,   # Maximum tokens in the response
        top_p=1,          # Nucleus sampling parameter
        frequency_penalty=0,  # Penalize new tokens based on existing frequency
        presence_penalty=0,   # Penalize based on presence of tokens in text so far
    )

    # Print the response content
    print(response.choices[0].message['content'])

except openai.error.OpenAIError as e:
    print(f"An error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
