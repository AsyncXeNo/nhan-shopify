import sys
import time
import random
import xml.etree.ElementTree as ET

import requests
from supabase import Client
from loguru import logger

from .supabase import fetch_data

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


def scrape_all_urls(base_sitemap_url: str) -> list[str]:
    response = requests.get(base_sitemap_url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        logger.critical(f'Failed to fetch sitemap {base_sitemap_url}: {response.status_code}')
        sys.exit(1)

    root = ET.fromstring(response.content)
    URLs = [elem.text for elem in root.iter() if elem.tag.endswith('loc')]

    final_product_urls = []

    product_urls = list(filter(
        lambda url: '.com/product/' in url or '.com/products/' in url,
        URLs
    ))

    final_product_urls += product_urls

    product_xml_urls = list(filter(
        lambda url: url.split('?')[0].strip('/').endswith('.xml') and 'products' in url, 
        URLs
    ))

    used_slugs = []
    unique_product_xml_urls = []
    
    for url in product_xml_urls:
        slug = url.split('?')[0].strip('/').split('/')[-1]
        if slug not in used_slugs:
            used_slugs.append(slug)
            unique_product_xml_urls.append(url)

    for url in unique_product_xml_urls:
        time.sleep(1)
        final_product_urls += scrape_all_urls(url)

    return list(set(final_product_urls))


def fetch_new_urls(base_sitemap_url: str, supabase_client: Client, table_name: str) -> list[str]:
    all_urls = scrape_all_urls(base_sitemap_url)

    for url in all_urls:
        if not url.endswith('/'):
            url += '/'
        if not url.startswith('https://'):
            url = 'https://' + url

    saved_urls = list(map(
        lambda record: record['url'],
        fetch_data(supabase_client, table_name)
    ))

    new_urls = list(filter(
        lambda url: url not in saved_urls,
        all_urls
    ))

    return new_urls