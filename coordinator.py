import geocoder
import sqlite3, os

import keys

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

cxn = sqlite3.connect(__location__+'\zillow.db')
c = cxn.cursor()
c.execute("Select * from listings")

curr_row = c.fetchone()
address = curr_row[1]
city = curr_row[-2]
zipcode = str(curr_row[-1])

print(geocoder.google(' '.join([address, city, zipcode])))

cxn.close()