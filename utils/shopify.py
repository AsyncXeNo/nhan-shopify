import requests


def format_for_shopify(product_data: dict) -> dict:
    
    images = [
        product_data['main_image']
    ]

    for image in product_data['images']:
        if not image in images:
            images.append(image)

    description_images = product_data.get('description_images')

    if description_images:
        for image in description_images:
            if not image in images:
                images.append(image)

    variants = []

    for variant in product_data['variants']:
        if variant.get('image') and variant.get('image') not in images:
            images.append(variant['image'])

        variants.append({
            'option1': variant['name'],
            'price': variant['price'],
            'image': {'src': variant['image']},
            'inventory_management': 'shopify',
            'inventory_quantity': 0,
            'inventory_policy': 'deny'
        })

    if not variants:
        variants.append({
            'price': product_data['price'],
            'inventory_management': 'shopify',
            'inventory_quantity': 0,
            'inventory_policy': 'deny'
        })

    unique_images = []
    for image_url in images:
        if image_url not in unique_images:
            unique_images.append(image_url)

    unique_images_formatted = list(map(
        lambda image: {'src': image.split('?')[0]},
        unique_images
    ))

    body_html = product_data['description'].replace('\n', '<br/>')

    return {
        'title': product_data['title'],
        'body_html': f'<p>{body_html}</p>',
        'images': unique_images_formatted,
        'variants': variants,
        'status': 'draft'
    }


def create_product(product_data: dict, shopify_api_key: str, shopify_subdomain: str) -> dict:
    
    headers = {
        'Content-type': 'application/json',
        'X-Shopify-Access-Token': shopify_api_key,
    }

    data = {
        'product': product_data
    }

    response = requests.post(f'https://{shopify_subdomain}/admin/api/2025-04/products.json', headers=headers, json=data)

    return response.json()['product']


def add_collection(product_id: int, collection_name: str, shopify_api_key: str, shopify_subdomain: str) -> dict:
    
    headers = {
        'X-Shopify-Access-Token': shopify_api_key
    }

    response = requests.get(f'https://{shopify_subdomain}/admin/api/2023-10/custom_collections.json?title={collection_name}')

    custom_collections = response.json().get('custom_collections')

    if custom_collections:
        headers = {
            'X-Shopify-Access-Token': shopify_api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'collect': {
                'product_id': product_id,
                'collection_id': custom_collections[0]['id']
            }
        }

        response = requests.post(f'https://{shopify_subdomain}/admin/api/2023-10/collects.json', headers=headers, json=data)
        return response.json()
    
    else:
        headers = {
            'X-Shopify-Access-Token': shopify_api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'custom_collection': {
                'title': collection_name
            }
        }

        response = requests.post(f'https://{shopify_subdomain}/admin/api/2023-10/custom_collections.json', headers=headers, json=data)
        custom_collection = response.json().get('custom_collection')
        collection_id = custom_collection.get('id')

        data = {
            'collect': {
                'product_id': product_id,
                'collection_id': collection_id
            }
        }
        
        response = requests.post(f'https://{shopify_subdomain}/admin/api/2023-10/collects.json', headers=headers, json=data)
        return response.json()
    

def add_sales_channels(product_id: str, shopify_api_key: str, shopify_subdomain: str) -> None:

    publication_ids = [
        '102341148965',
        '126488248613',
        '134054543653',
        '197864915237',
        '249506791717',
        '261355569445'
    ]

    for publication_id in publication_ids:

        headers = {
            'X-Shopify-Access-Token': shopify_api_key,
            'Content-Type': 'application/json'
        }

        graphql_query = {
            "query": """
            mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
              publishablePublish(id: $id, input: $input) {
                publishable {
                  __typename
                }
                userErrors {
                  field
                  message
                }
              }
            }
            """,
            "variables": {
            "id": f"gid://shopify/Product/{product_id}",
            "input": [
                {
                "publicationId": f"gid://shopify/Publication/{publication_id}"
                }
            ]
            },
            "operationName": "publishablePublish"
        }

        requests.post(
            f'https://{shopify_subdomain}/admin/api/2023-04/graphql.json',
            headers=headers,
            json=graphql_query
        )


def add_variant_images(original_variants_data: list, original_images_data: list, created_product_variants: list, created_product_images: list, shopify_api_key: str, shopify_subdomain: str) -> dict:

    # variants_and_images = []
    
    # for index, _ in enumerate(original_variants_data):
    #     try:
    #         original_variant_image = original_variants_data[index]['image']['src'].split('?')[0]
    #     except Exception:
    #         original_variant_image = None

    #     if not original_variant_image:
    #         variants_and_images.append({
    #             'id': created_product_variants[0]['id'],
    #             'image_id': created_product_images[0]['id']
    #         })
    #         break

    #     variants_and_images.append({
    #         'id': created_product_variants[index]['id'],
    #         'image_id': created_product_images[
    #             list(map(
    #                 lambda img: img['src'].split('?')[0],
    #                 original_images_data
    #             )).index(original_variant_image)
    #         ]['id']
    #     })

    src_to_image_id = {
        img['src'].split('?')[0]: img['id']
        for img in created_product_images
    }

    variants_and_images = []

    for idx, variant in enumerate(original_variants_data):
        raw_src = variant.get('image', {}).get('src')
        key = raw_src.split('?')[0] if raw_src else None

        if key and key in src_to_image_id:
            image_id = src_to_image_id[key]
            variant_id = created_product_variants[idx]['id']
        else:
            # fallback to first image if no exact match
            variant_id = created_product_variants[idx]['id']
            image_id = created_product_images[0]['id']

        variants_and_images.append({
            'id': variant_id,
            'image_id': image_id
        })

    for record in variants_and_images:
        headers = {
            'X-Shopify-Access-Token': shopify_api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'variant': {
                'id': record['id'],
                'image_id': record['image_id']
            }
        }

        response = requests.put(f'https://{shopify_subdomain}/admin/api/2023-04/variants/{record["id"]}.json', headers=headers, json=data)