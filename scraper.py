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
urla = ["https://www.zillow.com/mission-tx-78572/houses/", "https://www.zillow.com/mcallen-tx/houses", "https://www.zillow.com/homes/Pharr-TX_rb/","https://www.zillow.com/homes/Edinburg-TX_rb/"]

urlb = ["https://www.zillow.com/mcallen-tx/houses"]



urlBaseMission = ["""https://www.zillow.com/mission-tx-78572/houses/""" , """_p/?searchQueryState={"pagination":{"currentPage":""", """},"mapBounds":{"west":-98.49463776025391,"east":-98.2302792397461,"south":26.091682784797964,"north":26.285156790575897},"regionSelection":[{"regionId":92515,"regionType":7}],"mapZoom":12,"filterState":{"isMakeMeMove":{"value":false},"isCondo":{"value":false},"isMultiFamily":{"value":false},"isManufactured":{"value":false},"isLotLand":{"value":false},"isTownhouse":{"value":false}},"isListVisible":true,"isMapVisible":false}"""]

urlBaseMcAllen = ["""https://www.zillow.com/mcallen-tx/houses/""","""_p/?searchQueryState={"pagination":{"currentPage":""","""},"mapBounds":{"west":-98.317891,"east":-98.195389,"south":26.10213,"north":26.349834},"usersSearchTerm":"McAllen%20TX","regionSelection":[{"regionId":25818,"regionType":6}],"filterState":{"isAllHomes":{"value":true},"isMultiFamily":{"value":false},"isCondo":{"value":false},"isTownhouse":{"value":false},"isManufactured":{"value":false},"isLotLand":{"value":false}}}"""]

urlBasePharr = ["""https://www.zillow.com/pharr-tx/houses/""","""_p/?searchQueryState={"pagination":{"currentPage":""","""},"mapBounds":{"west":-98.229504,"east":-98.145055,"south":26.053268,"north":26.253715},"usersSearchTerm":"Pharr%20TX","regionSelection":[{"regionId":47082,"regionType":6}],"filterState":{"isMakeMeMove":{"value":false},"isAllHomes":{"value":true},"isCondo":{"value":false},"isMultiFamily":{"value":false},"isManufactured":{"value":false},"isLotLand":{"value":false},"isTownhouse":{"value":false}}}"""]

urlBaseEdinburg = ["""https://www.zillow.com/edinburg-tx/houses/""","""_p/?searchQueryState={"pagination":{"currentPage":""","""},"mapBounds":{"west":-98.498808,"east":-98.015619,"south":26.237148,"north":26.633589},"usersSearchTerm":"Edinburg%20TX","regionSelection":[{"regionId":4521,"regionType":6}],"filterState":{"isMakeMeMove":{"value":false},"isAllHomes":{"value":true},"isCondo":{"value":false},"isMultiFamily":{"value":false},"isManufactured":{"value":false},"isLotLand":{"value":false},"isTownhouse":{"value":false}}}"""]

urlList = [urlBaseMission, urlBaseMcAllen, urlBasePharr, urlBaseEdinburg]

for k,item in enumerate(urlList):
    #voodoo magic
    with requests.Session() as s:
        r = s.get(urla[k], headers=req_headers)

    soup = BeautifulSoup(r.content, 'lxml')

    #find max listings
    max_listings = int(re.findall("\d+",soup.find('span',{'class': 'result-count'}).text)[0])
    i = 0
    j = 1
    #scrape every listing
    while (i < max_listings):
        print("looping")
        if j is 1:
            url = urla[k]
        else:
            url = str(j).join(item)
        print(url)
        #voodoo magic
        with requests.Session() as s:
            r = s.get(url, headers=req_headers)
            j += 1

        soup = BeautifulSoup(r.content, 'lxml')

        #for every <a> element with the class "list-card-info"
        for li in soup.find_all('a', {'class': "list-card-info"}):
            try:
                price_raw = li.find('div', {'class': 'list-card-price'}).text
            except:
                i+=1
                continue
            
            price_list = re.findall("\d+", price_raw)
            try:
                price = int(''.join(price_list))
            except:
                i += 1
                continue

            list_card_details = li.find('ul', {'class': 'list-card-details'})
            info_list = list_card_details.find_all('li')
            try:
                bedrooms_raw, baths_raw, square_feet_raw = info_list[0].text, info_list[1].text, info_list[2].text
            except:
                i+=1
                continue

            try:
                bedrooms = int(re.findall("\d+",bedrooms_raw)[0])
            except:
                bedrooms = 0
            try:
                baths = int(re.findall("\d+", baths_raw)[0])
            except:
                baths = 0
            try:
                square_feet = int(''.join(re.findall("\d+", square_feet_raw)))
            except:
                square_feet = 0
            
            address_raw = li.find('h3', {'class': 'list-card-addr'}).text
            print(address_raw)
            try:
                address, city, zipcode_raw = address_raw.split(", ")
            except:
                i += 1
                continue

            try:
                zipcode = int(re.findall("\d+",zipcode_raw)[0])
            except:
                zipcode = 0

            sql11 = sql1.format(insert_address = address, insert_price =price, insert_bedrooms = bedrooms, insert_bathrooms = baths, insert_sqft = square_feet, insert_city = city, insert_zipcode = zipcode)
            sql21 = sql2.format(insert_address = address, insert_price =price, insert_bedrooms = bedrooms, insert_bathrooms = baths, insert_sqft = square_feet, insert_city = city, insert_zipcode = zipcode)
            c.execute(sql11)
            c.execute(sql21)
            cxn.commit()
            i += 1

        time.sleep(3)
        if (j * 30) > max_listings:
            break
    cxn.commit()
cxn.close()