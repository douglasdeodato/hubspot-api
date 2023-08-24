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

API_URL = 'https://api.hubapi.com/contacts/v1/lists/all/contacts/all'

headers = {
    'Authorization': f'Bearer {API_KEY}'
}

num_contacts_to_fetch = 10  # Set the desired number of contacts to fetch
contacts_fetched = 0  # Counter for the fetched contacts

all_contacts = []  # Store selected properties for all contacts here

try:
    offset = 0
    while contacts_fetched < num_contacts_to_fetch:
        response = requests.get(API_URL, params={'count': 100, 'offset': offset}, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP error responses
        contacts_data = response.json()
        contacts = contacts_data.get('contacts', [])

        if not contacts:
            break  # No more contacts to fetch

        # Collect contacts until the desired number is reached
        for contact in contacts:
            properties = contact['properties']
            identity_profiles = contact.get('identity-profiles', [])
            identity_profiles_data = []
            for identity in identity_profiles:
                identities = identity.get('identities', [])
                identities_data = []
                for identity_data in identities:
                    identity_type = identity_data.get('type', '')
                    identity_value = identity_data.get('value', '')
                    identities_data.append({
                        "type": identity_type,
                        "value": identity_value
                    })
                identity_profiles_data.append({
                    "vid": identity.get('vid', ''),
                    "identities": identities_data
                })

            contact_properties = {
                "id": contact['vid'],
                "firstname": properties.get('firstname', {}).get('value', ''),
                "lastname": properties.get('lastname', {}).get('value', ''),
                "email": properties.get('email', {}).get('value', ''),
                "createdate": properties.get('createdate', {}).get('value', ''),
                "lastmodifieddate": properties.get('lastmodifieddate', {}).get('value', ''),
                "archived": properties.get('archived', {}).get('value', ''),
                "identity_profiles": identity_profiles_data
            }
            all_contacts.append(contact_properties)
            contacts_fetched += 1

            if contacts_fetched >= num_contacts_to_fetch:
                break  # Stop fetching contacts

        offset += 100  # Increment offset for the next page

    # Render HTML template using Jinja2
    with open('templates/contacts.html', 'r') as template_file:
        template_content = template_file.read()
        template = Template(template_content)
        rendered_html = template.render(contacts=all_contacts)

    # Save rendered HTML to a file
    with open('contacts_index.html', 'w') as html_file:
        html_file.write(rendered_html)

    print("HTML table saved to contacts_index.html")

    # Save contact data as JSON
    with open('contacts_data.json', 'w') as json_file:
        json.dump(all_contacts, json_file, indent=2)

    print("Contact data saved to contacts_data.json")

except requests.exceptions.RequestException as e:
    error_message = f"Error fetching contacts: {e}"
    print(error_message)