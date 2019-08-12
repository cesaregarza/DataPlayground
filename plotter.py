import matplotlib.pyplot as plt
import numpy as np

import sqlite3, os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

cxn = sqlite3.connect(__location__+'\zillow.db')
c = cxn.cursor()

import_sql = "select price, bedrooms, baths, square_feet, lat, lon from listings"
c.execute(import_sql)
all_data = np.array(c.fetchall())

fig, axs = plt.subplots(1, 2, sharey = True, tight_layout = True)
n_bins = 25

axs[0].hist(all_data[0], bins=n_bins)
axs[1].hist(all_data[3], bins=n_bins)