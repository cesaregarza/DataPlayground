import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.request import urlopen
from bs4 import BeautifulSoup

import requests, sqlite3, os, re, time


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

cxn = sqlite3.connect(__location__+'\zillow.db')
c = cxn.cursor()

#sql commands
sql1 = """insert or ignore into listings(address, price, bedrooms, baths, square_feet, city, zipcode) values("{insert_address}",{insert_price},{insert_bedrooms},{insert_bathrooms},{insert_sqft},"{insert_city}",{insert_zipcode});"""
sql2 = """update listings 
set price = {insert_price}, bedrooms = {insert_bedrooms}, baths={insert_bathrooms}, square_feet = {insert_sqft}, city="{insert_city}",zipcode={insert_zipcode}
where address="{insert_address}";"""

#Headers so we can actually scrape
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36 OPR/62.0.3331.72'
}

#base list of URLs
urla = {"mission": "https://www.zillow.com/mission-tx-78572/houses/", "mcallen": "https://www.zillow.com/homes/McAllen-TX_rb/houses/", "pharr": "https://www.zillow.com/homes/Pharr-TX_rb/houses/", "edinburg": "https://www.zillow.com/homes/Edinburg-TX_rb/houses/"}

queryString = """{insert_page}_p/?searchQueryState={{"pagination":{{"currentPage":{insert_page}}},"mapBounds":{{"west":-98.449305,"east":-98.275612,"south":26.102146,"north":26.27471}},"usersSearchTerm":"78572","regionSelection":[{{"regionId":92515,"regionType":7}}],"filterState":{{"isMakeMeMove":{{"value":false}},"isAllHomes":{{"value":true}},"isLotLand":{{"value":{insert_lots}}},"isMultiFamily":{{"value":false}},"isManufactured":{{"value":{insert_manufactured}}},"isCondo":{{"value":{insert_condo}}}}}"""

#query settings
include_lots = "false"
is_manufactured = "false"
is_condo = "false"



#voodoo magic
with requests.Session() as s:
    url = urla["mission"]
    r = s.get(url, headers=req_headers)

soup = BeautifulSoup(r.content, 'lxml')

#find max listings
max_listings = int(re.findall("\d+",soup.find('span',{'class': 'result-count'}).text)[0])
i = 0
j = 1
#scrape every listing
while (i < 80):
    print("looping")
    #voodoo magic
    with requests.Session() as s:
        if j is 1:
            url = urla["mission"]
        else:
            qstring = queryString.format(insert_page = j, insert_lots = include_lots, insert_manufactured = is_manufactured, insert_condo = is_condo)
            url = urla["mission"] + qstring
            print(url)
        j += 1
        r = s.get(url, headers=req_headers)

    soup = BeautifulSoup(r.content, 'lxml')

    #for every <a> element with the class "list-card-info"
    for li in soup.find_all('a', {'class': "list-card-info"}):
        price_raw = li.find('div', {'class': 'list-card-price'}).text
        price_list = re.findall("\d+", price_raw)
        price = int(''.join(price_list))

        list_card_details = li.find('ul', {'class': 'list-card-details'})
        info_list = list_card_details.find_all('li')
        bedrooms_raw, baths_raw, square_feet_raw = info_list[0].text, info_list[1].text, info_list[2].text
        bedrooms = int(re.findall("\d+",bedrooms_raw)[0])
        baths = int(re.findall("\d+", baths_raw)[0])
        square_feet = int(''.join(re.findall("\d+", square_feet_raw)))
        
        address_raw = li.find('h3', {'class': 'list-card-addr'}).text
        print(address_raw)
        address, city, zipcode_raw = address_raw.split(", ")
        try:
            zipcode = int(re.findall("\d+",zipcode_raw)[0])
        except:
            zipcode = 0

        sql11 = sql1.format(insert_address = address, insert_price =price, insert_bedrooms = bedrooms, insert_bathrooms = baths, insert_sqft = square_feet, insert_city = city, insert_zipcode = zipcode)
        sql21 = sql2.format(insert_address = address, insert_price =price, insert_bedrooms = bedrooms, insert_bathrooms = baths, insert_sqft = square_feet, insert_city = city, insert_zipcode = zipcode)
        c.execute(sql11)
        c.execute(sql21)
        # cxn.commit()
        i += 1

    time.sleep(3)
# cxn.commit()
cxn.close()