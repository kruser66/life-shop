import os
import json
import requests
from environs import Env
from pprint import pprint
from random import choice

API_BASE_URL='https://api.moltin.com/v2'


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


def get_cart(access_token, cart_id):
    url_api = f'https://api.moltin.com/v2/carts/{cart_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = requests.get(url_api, headers=headers)
    response.raise_for_status()

    return response.json()


def delete_cart(access_token, cart_id):
    url_api = f'https://api.moltin.com/v2/carts/{cart_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.delete(url_api, headers=headers)
    # response.raise_for_status()

    return response


def add_item_to_cart(access_token, card_id, product):

    url = f'https://api.moltin.com/v2/carts/{card_id}/items'
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
    response = requests.post(url, headers=headers, data=json.dumps(params))
    # response.raise_for_status()
    return response.json()


def get_cart_items(access_token, card_id):

    url = f'https://api.moltin.com/v2/carts/{card_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    # response.raise_for_status()
    return response.json()


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
        'filename': response.json()['data']['link']['file_name']
    }

    return image_description


if __name__ == '__main__':

    env = Env()
    env.read_env()

    client_id = env.str('MOTLIN_CLIENT_ID')
    client_secret = env.str('MOTLIN_CLIENT_SECRET')

    access_token = client_credentials_access_token(client_id, client_secret)
    # print(access_token)

    products = fetch_products(access_token)
    product = choice(products)
    # pprint(product)
    # pprint(get_product_by_id(access_token, product['id']))

    image_url = take_product_image_url(access_token, product)
    print(image_url)
    # add_item_to_cart(access_token, 'id1234', product)
    #
    # items = get_cart_items(access_token, 'id1234')
    # pprint(items)
