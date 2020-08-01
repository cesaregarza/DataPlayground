# %%
import pandas as pd
import numpy as np

# %%

main_df = pd.read_csv('/Users/cesargarza/Dev/Data/last_fm.csv', header=None)
main_df.columns = ["Artist", "Album", "Song", "Date"]
main_df['Date'] = pd.to_datetime(main_df['Date'])
unique_songs = pd.read_csv('song_list_series.csv')
dedupe_output = pd.read_csv("dedupe_output.csv")
transform_list = pd.read_csv("dedupe_fix.csv")

# %%
mdf = pd.read_csv("last_fm.csv")

# %%
