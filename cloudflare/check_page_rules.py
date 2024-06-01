from dotenv import load_dotenv
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
ZONES = {}

def check_token_is_valid():
    # Check that token is active:
    request_url = BASE_URL + "/user/tokens/verify"

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ACCOUNT_API_TOKEN
    }

    request_response = requests.get(url=request_url, headers=request_headers).json()

    return request_response['success'] == True

def get_zones():
    # Get all the zones of the account
    request_url = BASE_URL + "/zones"

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ACCOUNT_API_TOKEN
    }

    request_response = requests.get(url=request_url, headers=request_headers).json()

    if request_response['success'] == True:
        for page in range(1, request_response['result_info']['total_pages'] + 1):
            for site in requests.get(url=request_url, headers=request_headers, params={'page': page}).json()['result']:
                ZONES[site['name']] = [site['id'], []]
    else:
        print('error')

def add_page_rules():
    # Get rules on every zone
    for zone in ZONES:
        request_url = BASE_URL + "/zones/" + ZONES[zone][0] + "/pagerules"

        request_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + ACCOUNT_API_TOKEN
        }

        request_response = requests.get(url=request_url, headers=request_headers).json()

        for action in request_response['result']:
            ZONES[zone][1].append(action['actions'][0]['id'])

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

    else:
        print("Token is invalid or is expired!")