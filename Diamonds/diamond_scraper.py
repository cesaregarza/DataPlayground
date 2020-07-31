# %%
import pandas as pd
import numpy as np

import sqlite3
conn = sqlite3.connect("diamonds.db")
cur = conn.cursor()

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# %%
class BlueNileScraper:
    def __init__(self):
        self.driver =   webdriver.Firefox()
        self.wait =     WebDriverWait(self.driver, 10)
    
    def intify(self, string):
        return int("".join([s for s in list(string) if s.isdigit()]))
    
    def price_intify(self, string):
        stri = ""
        for s in string[::-1]:
            if s.isdigit():
                stri += s
            elif s == "$":
                break
        return int(stri[::-1])
    
    def click_button(self, button_name):
        button = self.driver.find_element_by_id(f"{button_name}-filter-button-med-lrg")
        button.click()
        return
    
    
    def scrape_data(self):
        self.driver.get("https://www.bluenile.com/diamond-search")

        #Click all the buttons!
        for i in ["Princess", "Emerald", "Asscher", "Cushion", "Marquise", "Radiant", "Oval", "Pear", "Heart"]:
            self.click_button(i)

        #Find total diamond count
        raw_diamond_count = self.driver.find_element_by_class_name("diamond-count").get_attribute('innerHTML')
        inner_text = BeautifulSoup(raw_diamond_count).get_text()
        diamond_count = self.intify(inner_text)
        
        count = 0
        self.df = pd.DataFrame(columns=["Shape", "Price", "Carat", "Cut", "Color", "Clarity"])


        while count < diamond_count:
            #wait to grab until grid-body loads
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "grid-body")))
            self.driver.execute_script("window.scrollBy(0, window.innerHeight * 5);")
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "grid-alert")))
            #grab and start parsing grid-body
            ccount = 0
            
            while ccount < 15:
                ccount += 1
                self.driver.execute_script("window.scrollBy(0, window.innerHeight * 5);")
                time.sleep(0.05)
            
            time.sleep(2 if count < 40000 else 1.5 if count < 80000 else 1)
            page_table = self.driver.find_element_by_class_name('grid-body').get_attribute('innerHTML')
            #Soup will help us find what we need
            page_soup = BeautifulSoup(page_table)
            
            #create a list
            page_list = page_soup.find_all('div', {'class': 'grid-row'})
            count += len(page_list)        

            #iterate through said list, grabbing the necessary information
            for row in page_list:
                shape =     row.find('div', {'class': 'row-cell shape'}).get_text()
                price =     row.find('div', {'class': 'row-cell price'}).get_text()
                carat =     row.find('div', {'class': 'row-cell carat'}).get_text()
                cut =       row.find('div', {'class': 'row-cell cut'}).get_text()
                color =     row.find('div', {'class': 'row-cell color'}).get_text()
                clarity =   row.find('div', {'class': 'row-cell clarity'}).get_text()

                #fix formatting
                price = self.price_intify(price)
                carat = float(carat)
                cut = cut[:len(cut) // 2]
                
                #append row to the dataframe
                self.df = self.df.append(pd.Series([shape, price, carat, cut, color, clarity], index=self.df.columns), ignore_index=True)

            max_price = self.df['Price'].max()
            self.driver.execute_script("window.scrollTo(0,0);")

            price_min_field = self.driver.find_element_by_name("price-min-input")
            price_min_field.clear()
            price_min_field.send_keys(str(max_price))
            price_min_field.send_keys(Keys.RETURN)

        return self.df
    
        
# %%
a = BlueNileScraper()
b = a.scrape_data()

# %%
count = 0
maximum = 200000

while count < maximum:
    #wait to grab until grid-body loads
    a.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "grid-body")))
    a.driver.execute_script("window.scrollBy(0, window.innerHeight * 5);")
    a.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "grid-alert")))
    #grab and start parsing grid-body
    ccount = 0
    
    while ccount < 15:
        ccount += 1
        a.driver.execute_script("window.scrollBy(0, window.innerHeight * 5);")
        time.sleep(0.05)
    
    time.sleep(2 if count < 40000 else 1.5 if count < 80000 else 1)
    page_table = a.driver.find_element_by_class_name('grid-body').get_attribute('innerHTML')
    #Soup will help us find what we need
    page_soup = BeautifulSoup(page_table)
    
    #create a list
    page_list = page_soup.find_all('div', {'class': 'grid-row'})
    count += len(page_list)        

    #iterate through said list, grabbing the necessary information
    for row in page_list:
        shape =     row.find('div', {'class': 'row-cell shape'}).get_text()
        price =     row.find('div', {'class': 'row-cell price'}).get_text()
        carat =     row.find('div', {'class': 'row-cell carat'}).get_text()
        cut =       row.find('div', {'class': 'row-cell cut'}).get_text()
        color =     row.find('div', {'class': 'row-cell color'}).get_text()
        clarity =   row.find('div', {'class': 'row-cell clarity'}).get_text()

        #fix formatting
        price = a.price_intify(price)
        carat = float(carat)
        cut = cut[:len(cut) // 2]
        
        #append row to the dataframe
        a.df = a.df.append(pd.Series([shape, price, carat, cut, color, clarity], index=a.df.columns), ignore_index=True)

    last_price = a.df.loc[len(a.df) - 1, "Price"]
    a.driver.execute_script("window.scrollTo(0,0);")

    price_min_field = a.driver.find_element_by_name("price-min-input")
    price_min_field.clear()
    price_min_field.send_keys(str(last_price))
    price_min_field.send_keys(Keys.RETURN)


# %%
