# %%
import pandas as pd
import numpy as np

import sqlite3
conn = sqlite3.connect("..\diamonds.db")
cur = conn.cursor()

# %%
df = pd.read_sql("SELECT * FROM MAIN_DB", conn).drop(columns=["index"])


# %%
#Remap values for Color Grade
alphabet = "DEFGHIJKLMNOPQRSTUVWXYZ"
color_remap_dict = {x: i for i,x in enumerate(alphabet)}
df['Color'] = df['Color'].map(color_remap_dict)

#Remap values for Clarity Grade
clarity_list = ["FL", "IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I"]
clarity_remap_dict = {x: i for i,x in enumerate(clarity_list)}
df['Clarity'] = df['Clarity'].map(clarity_remap_dict)

#Remap values for Cut Grade
cut_remap_dict = {
    "Super Ideal": 0,
    "Astor Id": 0,
    "Ideal": 1,
    "Very Good": 2,
    "Good": 3,
    "Fair": 4
}
df['Cut'] = df['Cut'].map(cut_remap_dict)
# %%
four_cs = ["Carat", "Color", "Clarity", "Cut"]
round_df = df.loc[df['Shape'] == "Round", [*four_cs, "Price"]]

# %%
