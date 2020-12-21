# %%
import requests
from last_fm_secrets import *
import time
import pandas as pd

class Function_Dictionary_Class:
    user_agent = "Halcyon"
    api_key    = api_key
    secret     = secret
    api_root_url = "http://ws.audioscrobbler.com/2.0"
    method       = "user.getRecentTracks"
    user         = username
    json         = "json"
    root_key     = "recenttracks"
    attributes   = "@attr"
    tracks       = "track"
    mb_id        = "mbid"
    artist       = "artist"
    name         = "name"
    album        = "album"
    date         = "date"
    uts          = "uts"
    text         = "#text"

    class DataFrame_Columns_Class:
        track_id    = "track_id"
        artist_id   = "artist_id"
        album_id    = "album_id"
        track_name  = "track_name"
        artist_name = "artist_name"
        album_name  = "album_name"
        date        = "date"
    
    def __init__(self):
        self.df_columns = self.DataFrame_Columns_Class()

func_dict = Function_Dictionary_Class()

headers = {
    "user-agent": func_dict.user_agent
}

payload = {
    "api_key": func_dict.api_key,
    "method": func_dict.method,
    "format": func_dict.json,
    "limit": 200,
    "user": func_dict.user,
    "extended": 1,
    "page": 1
}

# %%
r = requests.get(func_dict.api_root_url, headers=headers, params=payload)
r.status_code
# %%
def retrieve_page(user_name, page):
    payload = {
        "api_key": func_dict.api_key,
        "method": func_dict.method,
        "format": func_dict.json,
        "limit": 200,
        "user": user_name,
        "extended": 1,
        "page": page
    }

    r = requests.get(func_dict.api_root_url, headers=headers, params=payload)
    retrieved_json = r.json()
    attributes = retrieved_json[func_dict.root_key][func_dict.attributes]
    if page > int(attributes['totalPages']):
        raise ValueError("Exceeded total number of pages")

    return retrieved_json[func_dict.root_key][func_dict.tracks]

def parse_page(page_data):
    
    temp_list = []

    for entry in page_data:
        temp_list.append({
            func_dict.df_columns.track_name:    entry[func_dict.name],
            func_dict.df_columns.track_id:      entry[func_dict.mb_id],
            func_dict.df_columns.artist_name:   entry[func_dict.artist][func_dict.name],
            func_dict.df_columns.artist_id:     entry[func_dict.artist][func_dict.mb_id],
            func_dict.df_columns.album_name:    entry[func_dict.album][func_dict.text],
            func_dict.df_columns.album_id:      entry[func_dict.album][func_dict.mb_id],
            func_dict.df_columns.date:          entry[func_dict.date][func_dict.uts]
        })
    
    return_df = pd.DataFrame(temp_list)
    return_df[func_dict.df_columns.date] = pd.to_datetime(return_df[func_dict.df_columns.date], unit="s")
    return return_df

# %%

def retrieve_all_data(user_name):

    #Retrieve first page, just for attribute examination
    payload = {
        "api_key": func_dict.api_key,
        "method": func_dict.method,
        "format": func_dict.json,
        "limit": 200,
        "user": user_name,
        "extended": 1,
    }
    r = requests.get(func_dict.api_root_url, headers=headers, params=payload)
    retrieved_json = r.json()
    attributes = retrieved_json[func_dict.root_key][func_dict.attributes]
    total_pages = int(attributes['totalPages'])

    list_of_dataframes = []
    for i in range(total_pages):
        print(f"\rPage {i + 1} of {total_pages}", end="")
        while True:
            try:
                page_data = retrieve_page(user_name, i + 1)
                break
            except KeyError:
                continue

        list_of_dataframes.append(parse_page(page_data))

        time.sleep(0.25)
    
    return pd.concat(list_of_dataframes, ignore_index=True)

# %%
df = pd.read_hdf("listener_df.h5", key="df")
# %%
