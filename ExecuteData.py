import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import urllib.parse

def generate_id_from_url(url, keywords):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path

    # Extract the product ID from the path
    id_string = path.split('/')[-2]

    id_string = f"{keywords}{id_string}"
    return id_string

async def get_data(url, table_name, connection):
    id_string = generate_id_from_url(url, table_name)
    print(id_string)
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    browser.maximize_window()
    row = check_if_product_exists(id_string, table_name, connection)
    try:
        item_og_price = browser.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]/span[2]').text
    except:
        item_og_price = None
        return
    if row and row[5]:  # Checking if the row exists and has an 'og_price' value
        if row[5]==item_og_price:
            print(row[5],item_og_price)
            return
        else :
            item_og_price = remove_non_numeric(item_og_price)
            await update_data(table_name,item_og_price,id_string,row,connection)
            return 
    
   

    try:
        item_title = browser.find_element(By.ID, 'productTitle').text
    except:
        item_title = None
        return -1

    try:
        item_review = browser.find_element(By.ID, 'acrCustomerReviewText').text
    except:
        item_review = None

    try:
        item_category = browser.find_element(By.CLASS_NAME, 'cat-link').text
    except:
        item_category = None

    try:
        item_sold_by = browser.find_element(By.XPATH, '//*[@id="merchant-info"]/a[1]/span').text
    except:
        item_sold_by = None

    try:
        item_discount_price = browser.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span/span/span[2]').text
    except:
        item_discount_price = None

    index = '1'
    flag2 = True
    items_stars_rating = []

    try:
        item_stars = browser.find_element(By.XPATH, '//*[@id="acrPopover"]/span[1]/a')
        item_stars.click()

        while flag2:
            items_star_rating = browser.find_element(By.XPATH, '//*[@id="histogramTable"]/tbody/tr[' + index + ']/td[3]/span[2]/a').text
            items_stars_rating.append(items_star_rating)
            index = str(int(index) + 1)
    except:
        flag2 = False

    try:
        item_img = browser.find_element(By.XPATH, '//*[@id="main-image-container"]/ul/li[1]')
        item_img.click()
        item_images = []
        sleep(3)
        i = '1'
        flag = True

        try:
            while flag:
                image = browser.find_element(By.XPATH, '//*[@id="ivLargeImage"]/img').get_attribute('src')
                item_images.append(image)
                image_src = browser.find_element(By.XPATH, '//*[@id="ivImage_' + i + '"]/div')
                image_src.click()
                sleep(1)
                i = str(int(i) + 1)
        except:
            flag = False
    except:
        item_images = []
        item_img = None
    
    await insert_data(id_string, table_name, item_title, item_review, item_category, item_sold_by, item_og_price, item_discount_price, items_stars_rating, item_images, url, connection)
    
    # Fetch and return the newly inserted row
    return check_if_product_exists(id_string, table_name, connection)

#Insert Data

async def insert_data(id, table_name, item_title, item_review, item_category, item_sold_by, item_og_price, item_discount_price, items_stars_rating, item_images, url, connection):
    # Remove percentage symbols from items_stars_rating values and convert to numeric
    items_stars_rating = [float(rating.replace('%', '')) for rating in items_stars_rating]
    item_og_price = remove_non_numeric(item_og_price)
    item_discount_price = remove_non_numeric(item_discount_price)

    current_date = datetime.datetime.now().date()  # Get the current date

    with connection.cursor() as cursor:
        cursor.execute('''
            INSERT INTO "{}" (id, title, review, category, sold_by, today_price, lowest_price, highest_price, non_discount_price, item_stars_rating, item_images_url, item_url, lowestpricetimestamp, highestpricetimestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::numeric[], %s, %s, %s, %s)
        '''.format(table_name), (
            id,
            item_title,
            item_review,
            item_category,
            item_sold_by,
            item_og_price if item_og_price else None,
            item_og_price if item_og_price else None,
            item_og_price if item_og_price else None,
            item_discount_price if item_discount_price else None,
            items_stars_rating,
            item_images,
            url,
            current_date,
            current_date
        ))
        connection.commit()
    print('inserted')

def remove_non_numeric(value):
    numeric_value = value.replace(",", "")
    numeric_value = numeric_value.replace("₹", "")
    return float(numeric_value)

def check_if_product_exists(id, table_name,connection):
    # Create a cursor to interact with the database
    with connection.cursor() as cursor:
        # Execute the query to check if the product exists
        cursor.execute('SELECT * FROM "{}" WHERE id = %s'.format(table_name), (id,))
        
        # Fetch the row if it exists
        row = cursor.fetchone()

        # Close the cursor and the database connection
        cursor.close()

    return row


import datetime

async def update_data(table_name, item_og_price, id, row, connection):
    with connection.cursor() as cursor:
        # Update today_price
        cursor.execute('''
            UPDATE "{}" SET today_price = %s WHERE id = %s
        '''.format(table_name), (item_og_price, id))

        lowest_price = row[6]  # Assuming lowest_price is at index 6 in the row
        highest_price = row[7]  # Assuming highest_price is at index 7 in the row

        current_date = datetime.datetime.now().date()  # Get the current date

        if lowest_price is None or item_og_price < lowest_price:
            # Update lowest_price and lowestpricetimestamp
            cursor.execute('''
                UPDATE "{}" SET lowest_price = %s, lowestpricetimestamp = %s WHERE id = %s
            '''.format(table_name), (item_og_price, current_date, id))
            lowest_price = item_og_price

        if highest_price is None or item_og_price > highest_price:
            # Update highest_price and highestpricetimestamp
            cursor.execute('''
                UPDATE "{}" SET highest_price = %s, highestpricetimestamp = %s WHERE id = %s
            '''.format(table_name), (item_og_price, current_date, id))
            highest_price = item_og_price

        connection.commit()
    print('Updated')
