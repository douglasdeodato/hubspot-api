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
    CONTACT_IDS = ['30551', '10101', '267851', '30122', '22854', '29160', '27620']  # Replace with actual contact IDs
    counties = []
    specialities = get_specialities()

    for contact_id in CONTACT_IDS:
        contact_data = fetch_contact_data(contact_id)
        if contact_data and 'properties' in contact_data and 'county' in contact_data['properties']:
            county = contact_data['properties']['county']['value']
            if county not in counties:
                counties.append(county)

    return render_template('search.html', counties=counties, specialities=specialities)

@app.route('/search', methods=['POST'])
def search():
    name = request.form['name'].lower()
    speciality = request.form['speciality'].lower()
    work_address = request.form['work_address'].lower()
    counties = request.form.getlist('county')

    CONTACT_IDS = ['30551', '10101', '267851', '30122', '22854', '29160', '27620']  # Replace with actual contact IDs
    search_results = []

    if any([name, speciality, work_address, counties]):
        for contact_id in CONTACT_IDS:
            contact_data = fetch_contact_data(contact_id)
            if contact_data and search_term_matches(contact_data, name, speciality, work_address, counties):
                search_results.append(contact_data)
    else:
        search_results = []

    return render_template('search_results.html', results=search_results)

@app.route('/contact_detail/<contact_id>')
def contact_detail(contact_id):
    contact_data = fetch_contact_data(contact_id)
    return render_template('contact_detail.html', contact_data=contact_data)

def fetch_contact_data(contact_id):
    api_url = API_URL_PATTERN.format(contact_id)
    response = requests.get(api_url, headers={'Authorization': f'Bearer {API_KEY}'})
    if response.status_code == 200:
        return response.json()
    return None

def search_term_matches(contact_data, name, speciality, work_address, counties):
    fields_to_search = ['speciality', 'county']

    if not counties:
        counties = []

    for field in fields_to_search:
        if 'properties' in contact_data and field in contact_data['properties']:
            field_value = contact_data['properties'][field]['value'].lower()
            if (not name or name in field_value) and \
               (not speciality or speciality in field_value) and \
               (not work_address or work_address in field_value) and \
               (field == 'county' and ('county' not in contact_data['properties'] or contact_data['properties']['county']['value'] in counties)):
                return True
    return False

def get_specialities():
    CONTACT_IDS = ['30551', '10101', '267851', '30122', '22854', '29160', '27620']  # Replace with actual contact IDs
    specialities = set()

    for contact_id in CONTACT_IDS:
        contact_data = fetch_contact_data(contact_id)
        if contact_data and 'properties' in contact_data and 'speciality' in contact_data['properties']:
            speciality = contact_data['properties']['speciality']['value']
            specialities.add(speciality)

    return list(specialities)

if __name__ == '__main__':
    app.run(debug=True)
