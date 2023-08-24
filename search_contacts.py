import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
API_KEY = os.getenv('HUBSPOT_API_KEY')

if API_KEY is None:
    raise ValueError("HUBSPOT_API_KEY environment variable is not set")

# Define the API URL pattern
API_URL_PATTERN = 'https://api.hubapi.com/contacts/v1/contact/vid/{}/profile'

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    name = request.form['name'].lower()
    speciality = request.form['speciality'].lower()
    work_address = request.form['work_address'].lower()

    CONTACT_IDS = ['30551', '10101', '267851', '30122']  # Replace with actual contact IDs
    search_results = []

    if any([name, speciality, work_address]):
        for contact_id in CONTACT_IDS:
            contact_data = fetch_contact_data(contact_id)
            if contact_data and search_term_matches(contact_data, name, speciality, work_address):
                search_results.append(contact_data)
    else:
        search_results = []

    return render_template('search_results.html', results=search_results)


def fetch_contact_data(contact_id):
    api_url = API_URL_PATTERN.format(contact_id)
    response = requests.get(api_url, headers={'Authorization': f'Bearer {API_KEY}'})
    if response.status_code == 200:
        return response.json()
    return None

def search_term_matches(contact_data, name, speciality, work_address):
    fields_to_search = ['firstname', 'lastname', 'speciality', 'workaddress1']
    for field in fields_to_search:
        if 'properties' in contact_data and field in contact_data['properties']:
            field_value = contact_data['properties'][field]['value'].lower()
            if (not name or name in field_value) and \
               (not speciality or speciality in field_value) and \
               (not work_address or work_address in field_value):
                return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
