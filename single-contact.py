import os
import requests
import json
from jinja2 import Template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
API_KEY = os.getenv('HUBSPOT_API_KEY')

if API_KEY is None:
    raise ValueError("HUBSPOT_API_KEY environment variable is not set")

# List of contact IDs to fetch
CONTACT_IDS = ['30551', '10101', '267851', '30122']  # Replace with actual contact IDs

# Define the API URL pattern
API_URL_PATTERN = 'https://api.hubapi.com/contacts/v1/contact/vid/{}/profile'

all_contacts_data = {}  # Dictionary to store all contact data

headers = {
    'Authorization': f'Bearer {API_KEY}'
}

# Define a default value for missing fields
DEFAULT_VALUE = "N/A"

try:
    for contact_id in CONTACT_IDS:
        # Fetch the contact data using the current contact ID
        api_url = API_URL_PATTERN.format(contact_id)
        response = requests.get(api_url, headers=headers)
        
        # Check if the response is successful before proceeding
        if response.status_code == 200:
            contact_data = response.json()

            # Provide default values for missing fields
            for field in ['accreditation', 'firstname', 'lastname', 'email', 'speciality', 'directory___work_phone', 'workaddress1', 'hs_language']:
                if 'properties' in contact_data and field not in contact_data['properties']:
                    contact_data['properties'][field] = {'value': DEFAULT_VALUE}

            # Store the contact data in the dictionary
            all_contacts_data[contact_id] = contact_data

    # Save all contact data as a single JSON file
    with open('single-contact.json', 'w') as json_file:
        json.dump(all_contacts_data, json_file, indent=2)

    print("All contact data saved to single-contact.json")

    # Render HTML template using Jinja2
    with open('templates/single-contact-template.html', 'r') as template_file:
        template_content = template_file.read()
        template = Template(template_content)
        rendered_html = template.render(contacts=all_contacts_data)

    # Save rendered HTML to a file
    with open('single-contact.html', 'w') as html_file:
        html_file.write(rendered_html)

    print("HTML contact info saved to single-contact.html")

except requests.exceptions.RequestException as e:
    error_message = f"Error fetching contact: {e}"
    print(error_message)
