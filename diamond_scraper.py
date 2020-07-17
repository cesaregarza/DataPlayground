# %%
import pandas as pd
import numpy as np

import sqlite3
conn = sqlite3.connect("diamonds.db")
cur = conn.cursor()


# %%
#Read database
df = pd.read_sql("SELECT * FROM MAIN_DB", conn)