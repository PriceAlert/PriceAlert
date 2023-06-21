import psycopg2
from ExecuteData import get_data
import asyncio

async def go_to_product(lnks, search_result, table_name):
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        host="dpg-ci6n1m6nqql0ld9ns4eg-a.singapore-postgres.render.com",
        database="pricealert",
        user="pricealert",
        password="AsNgIyrmVmcnVs5SmNJaj9gstWicJ8ec"
    )
    
    await create_table_if_not_exists(table_name, connection)
    
    tasks = []
    i=0
    for lnk in lnks:
        item = lnk.get_attribute("href")
        if item is not None:
            if search_result in item:
                i=i+1
                if(i==5):
                    break
                task = asyncio.create_task(get_data(item, table_name, connection))
                tasks.append(task)

    await asyncio.gather(*tasks)

# Create a table if it doesn't exist
async def create_table_if_not_exists(table_name, connection):
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "{}" (
                id TEXT PRIMARY KEY,
                title TEXT,
                review TEXT,
                category TEXT,
                sold_by TEXT,
                today_price DECIMAL,
                lowest_price DECIMAL,
                highest_price DECIMAL,
                non_discount_price DECIMAL,
                item_stars_rating numeric[],
                item_images_url TEXT[],
                item_url TEXT,
                lowestpricetimestamp TIMESTAMP,
                highestpricetimestamp TIMESTAMP
            )
        '''.format(table_name))
        connection.commit()
