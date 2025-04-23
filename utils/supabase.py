import sys

from loguru import logger
from supabase import Client


def fetch_data(supabase_client: Client, table_name: str, batch_size: int = 1000) -> list[dict]:
    all_data = []
    start = 0

    while True:
        end = start + batch_size - 1
        response = supabase_client.table(table_name).select('*').range(start, end).execute()
        
        if not response.data:
            break

        all_data.extend(response.data)

        # If we got fewer records than batch_size, we're done
        if len(response.data) < batch_size:
            break

        start += batch_size

    return all_data


def fetch_data_by_id(supabase_client: Client, table_name: str, record_id: str) -> dict:
    try:
        response = supabase_client.table(table_name).select('*').eq('id', record_id).execute()
        if not response.data:
            logger.critical(f'No data found in {table_name} for ID {record_id}.')
            sys.exit(1)
        return response.data[0]
    except Exception as e:
        logger.critical(f'Error fetching data from {table_name} by ID {record_id}: {e.message}.')
        sys.exit(1)


def insert_data(supabase_client: Client, table_name: str, data: dict) -> dict:
    try:
        response = supabase_client.table(table_name).insert(data).execute()
        if not response.data:
            logger.critical(f'No data inserted into {table_name}.')
            sys.exit(1)
        return response.data[0]
    except Exception as e:
        logger.critical(f'Error inserting data into {table_name}: {e.message}.')
        sys.exit(1)


def update_data(supabase_client: Client, table_name: str, record_id: str, data: dict) -> dict:
    try:
        response = supabase_client.table(table_name).update(data).eq('id', record_id).execute()
        if not response.data:
            logger.critical(f'No data updated in {table_name} for ID {record_id}.')
            sys.exit(1)
        return response.data[0]
    except Exception as e:
        logger.critical(f'Error updating data in {table_name} for ID {record_id}: {e.message}.')
        sys.exit(1)


def delete_data(supabase_client: Client, table_name: str, record_id: str) -> None:
    try:
        response = supabase_client.table(table_name).delete().eq('id', record_id).execute()
        if not response.data:
            logger.critical(f'No data deleted from {table_name} for ID {record_id}.')
            sys.exit(1)
    except Exception as e:
        logger.critical(f'Error deleting data from {table_name} for ID {record_id}: {e.message}.')
        sys.exit(1)