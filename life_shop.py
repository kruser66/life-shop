import os
import json
import requests
from dotenv import load_dotenv
from pprint import pprint
from random import choice


def fetch_products(access_token):
    url = 'https://api.moltin.com/v2/products'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    products = requests.get(url, headers=headers)
    products.raise_for_status()

    return products.json()


def client_credentials_access_token(client_id, client_secret):
    url_api = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(url_api, data=data)
    response.raise_for_status()

    return response.json()['access_token']


def implicit_access_token(client_id):
    url_api = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }

    response = requests.post(url_api, data=data)
    response.raise_for_status()

    return response.json()['access_token']

def fetch_settings(access_token):
    url_api = f'https://api.moltin.com/v2/settings'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = requests.get(url_api, headers=headers)
    response.raise_for_status()

    return response.json()



def update_or_create_cart(access_token, cart_id):
    url_api = f'https://api.moltin.com/v2/carts/{cart_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = requests.get(url_api, headers=headers)
    response.raise_for_status()

    return response.json()



if __name__ == '__main__':

    load_dotenv()
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']

    # access_token = implicit_access_token(client_id)
    access_token = client_credentials_access_token(client_id, client_secret)

    products = fetch_products(access_token)
    # pprint(products['data'])

    cart = update_or_create_cart(access_token, 'id1234')
    pprint(cart)
    # exit()

    product = choice(products['data'])
    # pprint(product)

    url = 'https://api.moltin.com/v2/carts/id1234/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    params = {
        'data': {
            'id': product['id'],
            'type': 'cart_item',
            'quantity': 1,
        }
    }
    json_params = json.dumps(params)
    print(json_params)

    response = requests.post(url, headers=headers, json=json_params)
    response.raise_for_status()

    pprint(response.json())