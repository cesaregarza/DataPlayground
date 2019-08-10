from scipy.optimize import linprog
import numpy as np

import sqlite3, os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

cxn = sqlite3.connect(__location__+'\zillow.db')
c = cxn.cursor()

###
# First step, we're going to fill in zip codes. To do this we will generate a list of unique zip codes in the database
# Then, we're going to find the convex hull of the points for each unique zip code
# We extract all zip codes with the value of zero and locate within which convex hull it finds itself in and assign it that zip code
###

distinct_sql = "select distinct zipcode from listings"
c.execute(distinct_sql)
zip_list_raw = c.fetchall()
zip_list = []
for zipp in zip_list_raw:
    zip_list.append(zipp[0])

zip_sql = "select lat, lon from listings where zipcode = {insert_zipcode}"

zip_points = []
#Create a point cloud for each zip code.
for x in zip_list:
    if x is 0:
        continue
    
    c.execute(zip_sql.format(insert_zipcode = x))
    zip_points.append(np.array(c.fetchall()))


#Finds if point is in hull, thanks StackOverflow!
def in_hull(points, x):
    n_points = len(points)
    n_dim = len(x)
    c = np.zeros(n_points)
    A = np.r_[points.T,np.ones((1,n_points))]
    b = np.r_[x, np.ones(1)]
    lp = linprog(c, A_eq=A, b_eq=b)
    return lp.success

zero_sql = "select lat, lon from listings where zipcode = 0"
c.execute(zero_sql)
zero_list_raw = c.fetchall()
zero_list = []
for i in zero_list_raw:
    zero_list.append(np.array(i))

fix_zip_sql = """update listings
set zipcode = {insert_zipcode} where lat={insert_lat} and lon={insert_lon};"""

#Check if the point lands within the convex hull of the zip code. Imperfect, as it turns out zero zip code gives the wrong lat, lon from TAMU. But this allows correction!
for i in zero_list:
    for j,k in enumerate(zip_points):
        if in_hull(k, i):
            update_sql = fix_zip_sql.format(insert_zipcode = zip_list[j], insert_lat = i[0], insert_lon = i[1])
            c.execute(update_sql)
            cxn.commit()

cxn.close()