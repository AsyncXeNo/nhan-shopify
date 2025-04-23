#!venv/bin/python3

import time
import traceback

import utils.config as config
from utils.sitemap import fetch_new_urls
from utils.apify import run_and_wait_for_output
from utils.shopify import (format_for_shopify, 
                           create_product, 
                           add_collection, 
                           add_sales_channels, 
                           add_variant_images)
from utils.mail import send_email, prepare_email
from utils.supabase import insert_data

logger = config.logger
supabase_client = config.client


def main() -> None:

    logger.info('Starting script')

    updated_data = {}
    
    for index, website_data in enumerate(config.websites):
        logger.info(f'[{index+1}/{len(config.websites)}] Processing website: {website_data["name"]}')
        
        website_name = website_data['name']
        website_sitemap_url = website_data['sitemap']
        website_table_name = website_data['table_name']
        website_actor_id = website_data['actor_id']

        new_products = fetch_new_urls(website_sitemap_url, supabase_client, website_table_name)

        logger.debug(f'{website_name} - Found {len(new_products)} new products.')
        
        logger.info(f'{website_name} - Sending data to Apify actor.')
        start_time = time.time()
        output = run_and_wait_for_output(website_actor_id, new_products, config.APIFY_API_KEY)
        end_time = time.time()
        logger.debug(f'{website_name} - Apify actor completed in {end_time - start_time:.2f} seconds.')

        pairs = []

        for index, product_info in enumerate(output):
            logger.info(f'{website_name} - Processing product {index + 1}/{len(output)}.')

            formatted_data = format_for_shopify(product_info)
            formatted_images_data = formatted_data['images']
            formatted_variants_data = formatted_data['variants']
            
            created_product_data = create_product(formatted_data, config.SHOPIFY_API_KEY, config.SHOPIFY_SUBDOMAIN)
            created_product_images = created_product_data['images']
            created_product_variants = created_product_data['variants']

            add_sales_channels(created_product_data['id'], config.SHOPIFY_API_KEY, config.SHOPIFY_SUBDOMAIN)

            for collection in product_info['collections']:
                add_collection(created_product_data['id'], collection, config.SHOPIFY_API_KEY, config.SHOPIFY_SUBDOMAIN)

            add_variant_images(formatted_variants_data, formatted_images_data, created_product_variants, created_product_images, config.SHOPIFY_API_KEY, config.SHOPIFY_SUBDOMAIN)

            pairs.append({
                'Source URL': product_info['url'],
                'Shopify Admin URL': f'https://admin.shopify.com/store/ac4775/products/{created_product_data["id"]}'
            })

            insert_data(supabase_client, website_table_name, {
                'url': product_info['url'],
                'added_to_store': True,
            })

        updated_data[website_name] = pairs

    logger.info('Sending update email.')
    send_email(prepare_email(updated_data))
    logger.info('Script has run to completion.')
    
        
if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.error('An error occurred while running the script.')
        logger.error(f'\n{traceback.format_exc()}')
