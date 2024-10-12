# Get deals status daily from Airtable to analyse cheanges
# by the end of the week.

import requests, os, json
import datetime
from abstra.common import get_persistent_dir


CONTENT_TYPE = "application/json"
API_TOKEN = os.getenv("AIRTABLE_TOKEN")

persistent_dir = get_persistent_dir()
folder_path = persistent_dir / "deals-status-everyday"
save_path = folder_path / f"deals-status-{datetime.date.today()}.json"
formatted_deals = {}

# get the complete list of deals from Airtable
def list_all_deals() -> list:

    url = f"https://api.airtable.com/v0/appKHwTmUuNQbROsK/deals?view=Grid%20view"
    headers = {
       "Authorization": f"Bearer {API_TOKEN}",
    }

    # get API response
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lança uma exceção se a resposta contém um código de status de erro HTTP
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return []
    
    # convert response to json
    try:
        response_json = response.json()
    except ValueError:
        print("Erro ao decodificar a resposta JSON")
        return []
    
    records = response_json.get('records', [])

    # deal with pagination if there are more than 100 records
    while 'offset' in response_json:
        pagination_url = f"{url}&offset={response_json['offset']}"
        try:
            response = requests.get(pagination_url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a requisição: {e}")
            break

        records.extend(response_json.get('records', []))

    deals = [deal for deal in records]

    return deals


# get the complete list of deals and return a dict with the id as key and status as value
def separate_by_id(deals: list) -> dict:
    status_dict = {}
    status_dict['date'] = datetime.date.today().strftime("%Y-%m-%d")

    for deal in deals:
        deal_id = deal["id"]
        if deal_id is not None:
            status_dict[deal_id] = {'status': None, 'name': None}

            status_dict[deal_id]['status'] = deal["fields"].get("status", None)
            status_dict[deal_id]['name'] = deal["fields"].get("name", None)

    return status_dict


formatted_deals = separate_by_id(list_all_deals())

# save to json file
try:
    with open(save_path, 'w') as f:
        json.dump(formatted_deals, f, indent=4)
except FileNotFoundError:
    os.makedirs(folder_path)
    with open(save_path, 'w') as f:
        json.dump(formatted_deals, f, indent=4)
