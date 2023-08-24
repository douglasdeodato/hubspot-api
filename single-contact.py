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

# Define a default value for missing fields
DEFAULT_VALUE = "N/A"

def fetch_contact_data(contact_id):
    api_url = API_URL_PATTERN.format(contact_id)
    response = requests.get(api_url, headers={'Authorization': f'Bearer {API_KEY}'})
    if response.status_code == 200:
        return response.json()
    return None

def provide_default_values(contact_data):
    for field in ['accreditation', 'firstname', 'lastname', 'email', 'speciality', 'directory___work_phone', 'workaddress1', 'hs_language']:
        if 'properties' in contact_data and field not in contact_data['properties']:
            contact_data['properties'][field] = {'value': DEFAULT_VALUE}

def save_data_as_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)

def render_template_and_save(data, template_path, output_path):
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
        template = Template(template_content)
        rendered_html = template.render(contacts=data)
    with open(output_path, 'w') as html_file:
        html_file.write(rendered_html)

try:
    all_contacts_data = {}
    for contact_id in CONTACT_IDS:
        contact_data = fetch_contact_data(contact_id)
        if contact_data:
            provide_default_values(contact_data)
            all_contacts_data[contact_id] = contact_data

    save_data_as_json(all_contacts_data, 'single-contact.json')
    print("All contact data saved to single-contact.json")

    render_template_and_save(all_contacts_data, 'templates/single-contact-template.html', 'single-contact.html')
    print("HTML contact info saved to single-contact.html")

except requests.exceptions.RequestException as e:
    error_message = f"Error fetching contact: {e}"
    print(error_message)
