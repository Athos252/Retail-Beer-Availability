import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
import csv
import re
#import pyarrow
import pandas as pd
import os
from datetime import datetime
import subprocess
from urllib.parse import urljoin
import sys
import datetime
import random
import json
from time import sleep

base_url = 'https://www.liquormarts.ca'
counter = 0

# Fetch retail listing page
# Parse product availability data
# Save cleaned results to CSV

def get_store_data(soup):
    store_data = []

    # Find all rows in the table body
    rows = soup.find_all('tr', class_='views-row')

    for row in rows:
        # Extract store name
        store_name_tag = row.find('a')
        store_name = store_name_tag.text.strip() if store_name_tag else 'Unknown'

        # Extract quantity
        quantity_tag = row.find('td', class_='views-field views-field-quantity')
        quantity = quantity_tag.text.strip() if quantity_tag else '0'

        # Append the extracted data to the list
        store_data.append({
            'store_name': store_name,
            'quantity': quantity
        })

    return store_data

def get_next_page_url(soup):
    next_page_link = soup.find('li', class_='pager-next')
    if next_page_link:
        return base_url + next_page_link.find('a')['href']
    return None

def get_product_name(soup):
    product_name_div = soup.find('div', class_='field--name-field-web-description')
    if product_name_div:
        product_name = product_name_div.get_text(strip=True)
        print(f"Product Name: {product_name}")  # Debug print
        return product_name
    return None

def get_item_number_and_size(soup):
    item_number = ''
    size = ''
    
    # Find the div containing the product details
    product_details_div = soup.find('div', class_='product_basic_details')
    if product_details_div:
        # Find the paragraph within the div
        item_info_p = product_details_div.find('p')
        if item_info_p:
            # Extract spans within the paragraph
            spans = item_info_p.find_all('span')

            # Extract item number from the first span, if available
            if spans and len(spans) > 0:
                item_number_span = spans[0]
                item_number_match = re.search(r'Item # (\d+)', item_number_span.text)
                if item_number_match:
                    item_number = item_number_match.group(1)

            # Extract size from the last span, if available
            if spans and len(spans) > 2:
                size_span = spans[2]
                # Updated regex to match both single serve and multipack sizes
                size_match = re.search(r'(\d+\s*x\s*)?(\d+)\s*ml', size_span.text)
                if size_match:
                    size = size_match.group(0).strip()

    return item_number, size

def extract_store_data(store):
    store_name_tag = store.find('a', class_='store-link')
    store_name = store_name_tag.text.strip().split('  (+)')[0] + '  (+)'  # Stop the store name at '(+)'
    quantity = store.find('td', class_='views-field-quantity-2').text.strip()
    
    return store_name, quantity

import re

def get_producer(soup):
    producer_name_div = soup.find("div", class_="producer-name")

    if producer_name_div:
        # Get the text from the producer-name div
        producer_name = producer_name_div.text.strip()
        return producer_name

    return ''


def extract_category(soup):
    product_details_div = soup.find("div", class_="product_details")
    if product_details_div:
        category_title_span = product_details_div.find("span", class_="product_details_title", string="Category:")
        if category_title_span:
            category_detail_span = category_title_span.find_next_sibling("span", class_="product_details_detail")
            if category_detail_span:
                category = category_detail_span.text.strip()
                return category
    return ''

def extract_container_type(soup):
    product_details_div = soup.find("div", class_="product_details")
    if product_details_div:
        container_type_span = product_details_div.find("span", class_="product_details_title", string="Container:")
        if container_type_span:
            container_type_detail_span = container_type_span.find_next_sibling("span", class_="product_details_detail")
            if container_type_detail_span:
                container_type = container_type_detail_span.text.strip()
                return container_type
    return ''

def extract_alcohol_percentage(soup):
    product_details_div = soup.find("div", class_="product_details")
    if product_details_div:
        alcohol_percentage_title_span = product_details_div.find("span", class_="product_details_title", string="Alcohol:")
        if alcohol_percentage_title_span:
            alcohol_percentage_detail_span = alcohol_percentage_title_span.find_next_sibling("span", class_="product_details_detail")
            if alcohol_percentage_detail_span:
                alcohol_percentage = alcohol_percentage_detail_span.text.strip()
                return alcohol_percentage
    return ''

def get_country_and_region(soup):
    country = ''
    region = ''

    # Find the span with the country class
    country_span = soup.find('span', class_='product_details_detail country')
    if country_span:
        links = country_span.find_all('a')
        if len(links) >= 1:
            country = links[0].get_text(strip=True)
        if len(links) >= 2:
            region = links[1].get_text(strip=True)

    return country, region



def get_price(soup):
    product_price_div = soup.find("div", class_="product_price")

    regular_price = ''
    promo_price = ''

    if product_price_div:
        retail_price_div = product_price_div.find("div", class_="retail_price")
        promo_price_div = product_price_div.find("div", class_="promo_price")
        
        if retail_price_div:
            regular_price = retail_price_div.text.strip().replace('REG. $', '')
        else:
            regular_price = product_price_div.text.strip().replace('$', '')
        
        if promo_price_div:
            promo_price = promo_price_div.text.strip().replace('$', '')

    return regular_price, promo_price

def get_sale_info(soup):
    sale_type = ''
    bonus_miles = ''

    marketing_program_div = soup.find("div", class_="marketing_program")

    if marketing_program_div:
        marketing_tag_icon = marketing_program_div.find("div", class_="marketing_tag_icon")
        bonus_miles_span = marketing_program_div.find("span", class_="bonus_miles_number")

        if bonus_miles_span:
            bonus_miles = bonus_miles_span.text.strip()

        if marketing_tag_icon:
            href = marketing_tag_icon.find('a').get('href', '')

            if 'limited-time-offers' in href:
                sale_type = 'Limited Time Offer'
            elif 'hot-buy' in href:
                sale_type = 'Hot Buy'
            elif 'last-chance' in href:
                sale_type = 'Last Chance'
            elif 'air-miles-bonus-miles' in href:
                sale_type = 'Bonus Miles'
            elif 'air-miles-max-miles' in href:
                sale_type = 'Max Miles'
            elif 'air-miles-bonus-bundles' in href:
                sale_type = 'Bonus Bundles'

    return sale_type, bonus_miles


def get_next_page_url(soup):
    next_page_li = soup.find("li", class_="pager-next")

    if next_page_li:
        next_page_a = next_page_li.find("a")
        
        if next_page_a:
            next_page_url = next_page_a.get("href")

            if next_page_url:
                # Ensure the URL is absolute
                base_url = "https://www.liquormarts.ca"  # Change this if the base URL is different
                return urljoin(base_url, next_page_url)

    # If no next page is found, return None
    return None

def list_files_in_dir(directory):
    # get all files in directory
    files = os.listdir(directory)
    # filter out any non-txt files
    txt_files = [file for file in files if file.endswith(".txt")]
    return txt_files

def get_user_choices(files):
    # Check if command-line arguments were provided
    if len(sys.argv) > 2:
        choices = sys.argv[1] # get the first command-line argument
    else:
        # display the available files to the user
        print("Choose the file(s) you want to pull data from:")
        for i, file in enumerate(files, start=1):
            print(f"{i}. {file}")
        # Ask the user for input if no command-line arguments were provided
        choices = input("Enter the number(s) corresponding to your choice(s), separated by commas: ")
    # strip leading/trailing whitespaces from each choice and convert to int
    choices = [int(choice.strip()) for choice in choices.split(',')]
    return choices
    
def get_headers():
    # Rendomized headers to avoid ingest distruptions
    # Load the JSON file containing header options
    with open('headers.json') as file:
        header_options = json.load(file)

    # Randomly select headers
    random_user_agent = random.choice(header_options['User-Agent'])
    random_accept = random.choice(header_options['Accept'])
    random_accept_language = random.choice(header_options['Accept-Language'])
    random_referer = random.choice(header_options['Referer'])
    random_accept_encoding = random.choice(header_options['Accept-Encoding'])

    # Define custom headers with randomly selected values
    headers = {
        'User-Agent': random_user_agent,
        'Accept': random_accept,
        'Accept-Language': random_accept_language,
        'Referer': random_referer,
        'Accept-Encoding': random_accept_encoding,
    }

    return headers
    
if __name__ == "__main__":
    print("Collecting Data lists...")
    subprocess.run([sys.executable, "listmaker.py"])
    dir_name = "Data/productlists"

    # get list of files in directory
    files = list_files_in_dir(dir_name)

    # get user's choices
    choices = get_user_choices(files)
    
    urls = []
    # read data from the chosen files
    for choice in choices:
        with open(f"{dir_name}/{files[choice-1]}", "r") as file:
            url = file.readlines()
            urls.extend(url)  # extend the list with urls from the file

    # Check if command-line arguments were provided for date input
    if len(sys.argv) > 2:
        date_input = sys.argv[2] # get the second command-line argument
    else:
        # Ask the user for the date
        date_input = input("Enter the date for this data pull (YYYY-MM-DD) or a number of days to add/subtract (+/-n), or leave blank for today's date: ").strip()

    if date_input == '':
        # No input, use today's date
        current_date = datetime.date.today()
    elif date_input.startswith('+') or date_input.startswith('-'):
        # Adjust the current date by a number of days
        days_to_adjust = int(date_input)
        current_date = datetime.date.today() + datetime.timedelta(days=days_to_adjust)
    else:
        # Parse the entered date
        current_date = datetime.datetime.strptime(date_input, '%Y-%m-%d').date()


    # Convert date to string for use in file names
    current_date_str = current_date.strftime('%Y-%m-%d')
    #with open(input_file_name, "r") as file:
    #    urls = file.readlines()

    all_data = []

    for url in urls:
        while url:
            url = url.strip()
            headers = get_headers()
            print(f"")
            print(f"Scraping {url}")
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            product_name = get_product_name(soup)
            item_number, size = get_item_number_and_size(soup)
            producer_name = get_producer(soup)
            category = extract_category(soup)
            country, region = get_country_and_region(soup)
            regular_price, promo_price = get_price(soup)
            sale_type, bonus_miles = get_sale_info(soup)
            container = extract_container_type(soup)
            abv = extract_alcohol_percentage(soup)
            print(f"{product_name} {item_number} {size} {producer_name} {category} {country} {region} {regular_price} {promo_price} {sale_type} {bonus_miles} {container} {abv} ")

            #current_date = datetime.now().strftime('%Y-%m-%d')

            store_data_list = get_store_data(soup)

            # Iterate through each store data entry
            for store_data in store_data_list:
                store_name = store_data['store_name']
                try:
                    quantity_int = int(store_data['quantity'])
                except ValueError:
                    continue

                # Append the entry to all_data
                all_data.append((current_date, store_name, quantity_int, item_number, size, container, product_name, producer_name, category, abv, country, region, regular_price, promo_price, sale_type, bonus_miles))
            
            # Increment the counter
            counter += 1

            # Determine the pause duration with millisecond precision
            if counter % 5 == 0:
                # Every 5 loops, pause between 1 and 5 seconds (with decimals)
                pause_duration = random.uniform(0.1, 0.5)
            else:
                # Otherwise, pause between 1 and 2 seconds (with decimals)
                pause_duration = random.uniform(0.1, 0.2)

            sleep(pause_duration)  # Pauses the script for the generated duration
            url = get_next_page_url(soup)

    output_folder = "Data/Daily Pulls"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    data_frame = pd.DataFrame(all_data, columns=['Date', 'Store Name', 'Quantity', 'Item Number', 'Size', 'Container', 'Product Name', 'Producer Name', 'Category', 'ABV', 'Country', 'Region', 'Regular Price', 'Promo Price', 'Sale Type', 'Bonus Miles'])
    output_file_name = f"{output_folder}/DV Data Pull {current_date_str}.xlsx"
    data_frame.to_excel(output_file_name, index=False)

    output_folder = "Data/Import Files"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    import_data_frame = data_frame[['Date', 'Store Name', 'Quantity', 'Item Number', 'Regular Price', 'Promo Price', 'Sale Type', 'Bonus Miles']]
    import_output_file_name = f"DV Data Pull {current_date_str}_import.xlsx"
    import_data_frame.to_excel(os.path.join("Data", "Import Files", import_output_file_name), index=False)