import requests
from bs4 import BeautifulSoup
import re
import json
import os
import random
import openpyxl
from urllib.parse import urljoin
from openpyxl import Workbook
import time

counter = 0
base_url = "https://www.liquormarts.ca"
urls = [
    f'{base_url}/search-products/all?search_api_fulltext=&f%5B0%5D=category_type%3A1428&view_mode=list',  # All
]
file_names = ["All"]  # Add corresponding names for the files here

def get_next_page_url(soup):
    next_page_li = soup.find('li', class_='pager__item pager__item--next')
    if next_page_li:
        next_page_link = next_page_li.find('a')
        if next_page_link and 'href' in next_page_link.attrs:
            query_string = next_page_link['href']
            # Construct the full URL by appending the query string to the path
            full_url = f"{base_url}/search-products/all{query_string}"
            return full_url
    return None



def extract_data(a_tag):
    return a_tag.get('href', None)


for url, file_name in zip(urls, file_names):
    all_data = []

    while url:
        print(f"Fetching URL: {url}")
        attempts = 0
        success = False
        print(f"")        # Debugging print
        
        
        while attempts < 3 and not success:
            try:
                response = requests.get(url, timeout=10)
                # Check if the request was successful
                if response.status_code == 200:
                    success = True
                    print(f"Success!")
                    break
                else:
                    print(f"Received status code {response.status_code}, retrying...")
            except Exception as e:
               print(f"Error fetching URL: {e}, retrying...")
            attempts += 1
            time.sleep(2)  # wait 2 seconds before retry
                
        if not success:
            print(f"Failed to fetch URL after {attempts} attempts. Skipping.")
            break 



        soup = BeautifulSoup(response.content, 'html.parser')

        product_list_items = soup.find_all('a', class_='wrap-link')

        if not product_list_items:
            print("No product links found, but checking for next page URL.")
            break

        for item in product_list_items:
            data = extract_data(item)
            #print(f"")
            #print(extract_data(item))
            if data is not None:
                all_data.append(f"{base_url}{data}")

        # Get the next page URL
        url = get_next_page_url(soup)
        print(f"Next URL: {url}")  # Debugging print
        print(f"")
        
        
    if not os.path.exists("data/productlists"):
        os.makedirs("data/productlists")

    # write URLs to txt file
    print(f"Writting Files to List")
    with open(f"data/productlists/{file_name}_urls.txt", 'w') as file:
        for data in all_data:
            file.write(f"{data}\n")
