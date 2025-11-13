"""CouchDB utility functions"""
import base64
import requests
import urllib3
from flask import current_app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def encode_credentials(username, password):
    """Encode credentials for Basic Auth"""
    credentials = f"{username}:{password}"
    return base64.b64encode(credentials.encode()).decode()


def create_headers():
    """Create headers with authentication"""
    config = current_app.config
    return {
        "Accept": "application/json",
        "Authorization": f"Basic {encode_credentials(config['COUCHDB_USERNAME'], config['COUCHDB_PASSWORD'])}"
    }


def fetch_reports_by_contact_id(contact_id):
    """Fetch reports by contact ID from CouchDB"""
    try:
        config = current_app.config
        url = f"{config['COUCHDB_URL']}/_find"
        query = {
            "selector": {
                "fields.patient_id": contact_id,
            },
            "limit": 1000
        }

        current_app.logger.debug(f"Fetching reports from CouchDB for contact_id: {contact_id}")
        response = requests.post(url, json=query, headers=create_headers(), verify=False)
        if response.status_code != 200:
            current_app.logger.error(f"CouchDB request failed for contact_id: {contact_id}, status: {response.status_code}")
            return None

        data = response.json()
        filtered_docs = data.get('docs', [])
        current_app.logger.debug(f"Found {len(filtered_docs)} documents for contact_id: {contact_id}")
        return [{"doc": doc} for doc in filtered_docs] if filtered_docs else None
    except Exception as e:
        current_app.logger.error(f"Error fetching reports for contact_id: {contact_id}, error: {str(e)}", exc_info=True)
        return None

