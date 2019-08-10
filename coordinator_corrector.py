import sqlite3, os, csv

#Geocoding courtesy of Texas A&M Geoservices

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

cxn = sqlite3.connect(__location__+'\zillow.db')
c = cxn.cursor()

sql = """update listings
set lat = {insert_lat}, lon = {insert_lon} where address="{insert_address}";"""

#Add latitude and longitude to corresponding addresses for corrected zerozip_geocoding
with open('zerozip_geocoded.csv') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(csv_reader)
    for row in csv_reader:
        address = row[0]
        latitude = row[-3]
        longitude = row[-2]
        sql1 = sql.format(insert_lat = latitude, insert_lon = longitude, insert_address = address)
        c.execute(sql1)
        cxn.commit()
    
cxn.commit()

cxn.close()