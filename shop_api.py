import os
import json
import requests
from environs import Env
from pprint import pprint
from random import choice

API_BASE_URL='https://api.moltin.com/v2'


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


def fetch_products(access_token):
    url = 'https://api.moltin.com/v2/products'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    products = requests.get(url, headers=headers)
    products.raise_for_status()

    return products.json()['data']


def get_product_by_id(access_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    products = requests.get(url, headers=headers)
    products.raise_for_status()

    return products.json()['data']


def take_product_image_description(access_token, product) -> dict:

    file_id = product['relationships']['main_image']['data']['id']
    url_api = f'https://api.moltin.com/v2/files/{file_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url_api, headers=headers)
    response.raise_for_status()

    image_description = {
        'url': response.json()['data']['link']['href'],
        'filename': response.json()['data']['file_name']
    }

    return image_description


def get_cart(access_token, cart_id):
    url_api = f'https://api.moltin.com/v2/carts/{cart_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = requests.get(url_api, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def delete_cart(access_token, cart_id):
    url_api = f'https://api.moltin.com/v2/carts/{cart_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.delete(url_api, headers=headers)
    response.raise_for_status()

    return response


def add_product_to_cart(access_token, card_id, product_id, amount=1):

    items = get_cart_items(access_token, card_id)
    item = [item for item in items if item['product_id'] == product_id]

    if item:
        response = update_item_to_cart(access_token, card_id, product_id, item[0], amount)
    else:
        response = add_item_to_cart(access_token, card_id, product_id, amount)

    return response


def add_item_to_cart(access_token, card_id, product_id, amount):
    url = f'https://api.moltin.com/v2/carts/{card_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    params = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': amount,
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(params))
    return response.json()


def update_item_to_cart(access_token, card_id, product_id, item, amount):

    url = f'https://api.moltin.com/v2/carts/{card_id}/items/{item["id"]}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    params = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': item['quantity'] + amount,
        }
    }
    response = requests.put(url, headers=headers, data=json.dumps(params))
    return response.json()


def delete_item_from_cart(access_token, card_id, item_id):

    url = f'https://api.moltin.com/v2/carts/{card_id}/items/{item_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.delete(url, headers=headers)
    return response.json()


def get_cart_items(access_token, card_id):

    url = f'https://api.moltin.com/v2/carts/{card_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()['data']



def get_customers(access_token):
    url_api = 'https://api.moltin.com/v2/customers'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = requests.get(url_api, headers=headers)
    response.raise_for_status()

    return response.json()['data']

def add_customer(access_token, user):
    url = f'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    params = {
        'data': {
            'type': 'customer',
        }
    }
    params['data'].update(user)

    response = requests.post(url, headers=headers, data=json.dumps(params))
    response.raise_for_status()

    return response.json()

if __name__ == '__main__':

    env = Env()
    env.read_env()

    client_id = env.str('MOTLIN_CLIENT_ID')
    client_secret = env.str('MOTLIN_CLIENT_SECRET')

    access_token = client_credentials_access_token(client_id, client_secret)
    pprint(get_customers(access_token))
    exit()
    products = fetch_products(access_token)
    product = choice(products)
    add_product_to_cart(access_token, 123567, product)
    pprint(get_cart(access_token, 123567))
    delete_cart(access_token, 123567)