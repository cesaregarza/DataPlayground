import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

urla = {"mission": "https://www.zillow.com/mission-tx-78572", "mcallen": "https://www.zillow.com/homes/McAllen-TX_rb/", "pharr": "https://www.zillow.com/homes/Pharr-TX_rb/", "edinburg": "https://www.zillow.com/homes/Edinburg-TX_rb/"}

pagination = "_p"

# html = urlopen(url["mission"])

with requests.Session() as s:
    url = urla["mission"]
    r = s.get(url, headers=req_headers)

soup = BeautifulSoup(r.content, 'lxml')

for li in soup.find_all('a', {'class': "list-card-info"}):
    price = li.find('div', {'class': 'list-card-price'}).text
    list_card_details = li.find('ul', {'class': 'list-card-details'})
    info_list = list_card_details.find_all('li')
    bedrooms, baths, square_feet = info_list[0].text, info_list[1].text, info_list[2].text

    print(price, bedrooms, baths, square_feet)