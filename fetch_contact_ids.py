import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
API_KEY = os.getenv('HUBSPOT_API_KEY')

if API_KEY is None:
    raise ValueError("HUBSPOT_API_KEY environment variable is not set")

# Define the API URL pattern
API_URL = 'https://api.hubapi.com/contacts/v1/lists/all/contacts/all'

# Set the headers and query parameters for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}'
}
params = {
    'count': 200
}

# Make the API request
response = requests.get(API_URL, headers=headers, params=params)

# Parse the response JSON
data = response.json()

# Extract contact IDs from the response
CONTACT_IDS = [contact['vid'] for contact in data['contacts']]

# Save the contact IDs to a JSON file with proper indentation
with open('contact_ids.json', 'w') as json_file:
    json.dump(CONTACT_IDS, json_file, indent=4)

print("Contact IDs saved to 'contact_ids.json'")
