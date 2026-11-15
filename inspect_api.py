import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('CDSE_USER')
PASSWORD = os.getenv('CDSE_PASSWORD')

auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
response = requests.post(auth_url, data={
    'client_id': 'cdse-public',
    'username': USER,
    'password': PASSWORD,
    'grant_type': 'password'
})
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get a few Sentinel-1 products to see their attributes
search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
# Filter by collection and a recent date to avoid AUX data if possible
filter_query = "Collection/Name eq 'SENTINEL-1' and ContentDate/Start gt 2026-03-01T00:00:00.000Z"
params = {'$filter': filter_query, '$top': 5, '$expand': 'Attributes'}

print(f"Searching with filter: {filter_query}")
res = requests.get(search_url, params=params, headers=headers)
if res.status_code == 200:
    data = res.json()
    for item in data.get('value', []):
        print(f"Product: {item['Name']}")
        for attr in item.get('Attributes', []):
            if attr['Name'] in ['productType', 'ProductType']:
                print(f"  {attr['Name']}: {attr['Value']}")
else:
    print(f"Error {res.status_code}: {res.text}")
