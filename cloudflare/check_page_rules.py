from dotenv import load_dotenv
from requests.exceptions import RequestException
from typing import Dict, List, Union
import os
import requests

# Load environment variables
load_dotenv()

# Assing environment variables to local variables
BASE_URL = os.getenv('BASE_URL')
ACCOUNT_API_TOKEN = os.getenv('ACCOUNT_API_TOKEN')

# Global variables
# This variable will contain all the information needed to save the zone file
# Each element will have the following information
# Key: Website, ex. viventura.us
# Value: Array with 2 elements
#
# Position 0 -> Id of the zone
# Position 1 -> Array with Page Rules
ZONES: Dict[str, Union[str, List[str]]] = {}

def check_token_is_valid() -> bool:
    """Check that the API token is active and valid."""
    request_url = f"{BASE_URL}/user/tokens/verify"

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCOUNT_API_TOKEN}"  
    }

    try:
        response = requests.get(url=request_url, headers=request_headers)
        response.raise_for_status()
        return response.json().get('success', False)

    except RequestException as e:
        print(f"Error verifying token: {e}")
        return False


def get_zones() -> None:
    """Retrieve all the zones of the account."""
    request_url = f"{BASE_URL}/zones"

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCOUNT_API_TOKEN}"
    }
    try:
        response = requests.get(url=request_url, headers=request_headers)
        response.raise_for_status()
        response_json = response.json()

        if response_json.get('success', False):
            total_pages = response_json['result_info']['total_pages']
            with requests.Session() as session:
                session.headers.update(request_headers)
                for page in range(1, total_pages + 1):
                    page_response = session.get(url=request_url, params={'page': page}).json()
                    for site in page_response['result']:
                        ZONES[site['name']] = [site['id'], []]

    except RequestException as e:
        print(f"Error fetching zones: {e}")


def add_page_rules():
    """Fetch and add page rules for each zone."""
    with requests.Session() as session:
        session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ACCOUNT_API_TOKEN}"
        })

        for zone_name, zone_data in ZONES.items():
            zone_id = zone_data[0]
            request_url = f"{BASE_URL}/zones/{zone_id}/pagerules"

            try:
                response = session.get(url=request_url)
                response.raise_for_status()
                response_json = response.json()

                if response_json.get('success', False):
                    for action in response_json['result']:
                        if 'actions' in action and action['actions']:
                            ZONES[zone_name][1].append(action['actions'][0]['id'])

            except RequestException as e:
                print(f"Error fetching page rules for zone {zone_name}: {e}")

def show_zones():
    for x in ZONES:
        print(f"{ x } - { ZONES[x][0] } - { ZONES[x][1] }")

if __name__ == "__main__":
    if check_token_is_valid():
        print("Token is Valid!")

        print("----- Checking Page rules of domains...")

        # Will obtain all the Zones available on the account
        get_zones()

        # Will add all the Page Rules that are available on each domain
        add_page_rules()

        # Shows all the zones and their data.
        show_zones()

        # Clear variables
        os.environ.pop("BASE_URL")
        os.environ.pop("ACCOUNT_API_TOKEN")


    else:
        print("Token is invalid or is expired!")