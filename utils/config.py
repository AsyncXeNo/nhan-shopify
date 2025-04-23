import os
import sys
from datetime import datetime


# Run data
websites = [
    {
        'name': 'saranghello',
        'sitemap': 'https://saranghello.com/sitemap.xml',
        'table_name': 'saranghello_product_urls',
        'actor_id': 'MwucoxJ4GfR4wjMh3'
    },
    {
        'name': 'cokodive',
        'sitemap': 'https://cokodive.com/sitemap.xml',
        'table_name': 'cokodive_product_urls',
        'actor_id': 'Hi2oQbKQFSASpwyYn'
    },
    {
        'name': 'choicemusicla',
        'sitemap': 'https://choicemusicla.com/sitemap.xml',
        'table_name': 'choicemusicla_product_urls',
        'actor_id': '88MiFGs1Nc4QmdHjG'
    },
    {
        'name': 'kpop2u',
        'sitemap': 'https://kpop2u-unnie.com/sitemap.xml',
        'table_name': 'kpop2u_product_urls',
        'actor_id': 'TjYL3E7W1DHMZI0KV'
    },
    {
        'name': 'kpopusaonline',
        'sitemap': 'https://kpopusaonline.com/sitemap.xml',
        'table_name': 'kpopusaonline_product_urls',
        'actor_id': '3TPQLr6pD4gQugoiT'
    },
    {
        'name': 'musicplaza',
        'sitemap': 'https://musicplaza.com/sitemap.xml',
        'table_name': 'musicplaza_product_urls',
        'actor_id': 'bZMHCbBjwpiHcdbLM'
    },
    {
        'name': 'subkshop',
        'sitemap': 'https://subkshop.com/sitemap.xml',
        'table_name': 'subkshop_product_urls',
        'actor_id': 'ReMwg17LjdbIz1arC'
    }
]


# Set up logging
from loguru import logger

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') 
log_filename = f'logs/{timestamp}.log'

logger.remove()
logger.add(sys.stderr, format='<green>[{elapsed}]</green> <level>{level} > {message}</level>')
logger.add(log_filename, mode='w', format='[{elapsed}] {level} > {message}')

logger.debug('Logged initialized.')


# Load ENV
from dotenv import load_dotenv

load_dotenv()

APIFY_API_KEY = os.getenv('APIFY_API_KEY')

SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_SECRET_KEY = os.getenv('SHOPIFY_SECRET_KEY')
SHOPIFY_SUBDOMAIN = os.getenv('SHOPIFY_SUBDOMAIN')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

RESEND_API_KEY = os.getenv('RESEND_API_KEY')

if all([APIFY_API_KEY, SHOPIFY_API_KEY, SHOPIFY_SECRET_KEY, SHOPIFY_SUBDOMAIN, SUPABASE_URL, SUPABASE_KEY, RESEND_API_KEY]):
    logger.debug('ENV loaded.')
else:
    logger.critical(f'Invalid ENV variables.')
    logger.info('Please check your .env file, exiting.')
    sys.exit(1)

# Supabase connection
from supabase import create_client, Client

client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.debug('Supabase client created.')