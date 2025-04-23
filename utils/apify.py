import sys

import time
import requests

from loguru import logger


def start_actor(actor_id, urls, apify_api_key):

    data = {
        'urls': list(map(
            lambda url: { 'url': url },
            urls
        ))
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {apify_api_key}'
    }

    response = requests.post(f'https://api.apify.com/v2/acts/{actor_id}/runs',
                  headers=headers,
                  json=data)

    return response.json()['data']


def get_run(run_id, apify_api_key):

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {apify_api_key}'
    }
    
    response = requests.get(f'https://api.apify.com/v2/actor-runs/{run_id}', headers=headers)

    return response.json()['data']


def get_items(dataset_id):

    response = requests.get(f'https://api.apify.com/v2/datasets/{dataset_id}/items?format=json')
    return response.json()[0]['urls']


def run_and_wait_for_output(actor_id, urls, apify_api_key):
    run = start_actor(actor_id, urls, apify_api_key)
    run_id = run['id']
    dataset_id = run['defaultDatasetId']

    while True:
        time.sleep(10)
        run = get_run(run_id, apify_api_key)
        if run['status'] == 'SUCCEEDED':
            break
        elif run['status'] == 'FAILED':
            logger.critical(f'Actor run (id:{actor_id}, run_id:{run_id}) failed.')
            sys.exit(1)

    return get_items(dataset_id)