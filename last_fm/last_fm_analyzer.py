# %%
import requests
from last_fm_secrets import *
import time
import pandas as pd
import math

class Function_Dictionary_Class:
    user_agent = "Halcyon"
    api_key    = api_key
    secret     = secret
    api_root_url        = "http://ws.audioscrobbler.com/2.0"
    method              = "user.getRecentTracks"
    user                = username
    json                = "json"
    root_key            = "recenttracks"
    attributes          = "@attr"
    tracks              = "track"
    mb_id               = "mbid"
    artist              = "artist"
    artists             = "artists"
    name                = "name"
    album               = "album"
    date                = "date"
    uts                 = "uts"
    text                = "#text"
    idd                 = "id"
    release_date        = "release_date"
    total_tracks        = "total_tracks"
    duration            = "duration_ms"
    explicit            = "explicit"
    popularity          = "popularity"
    danceability        = "danceability"
    energy              = "energy"
    key                 = "key"
    loudness            = "loudness"
    mode                = "mode"
    speechiness         = "speechiness"
    acousticness        = "acousticness"
    instrumentalness    = "instrumentalness"
    liveness            = "liveness"
    valence             = "valence"
    tempo               = "tempo"
    time_signature      = "time_signature"

    class DataFrame_Columns_Class:
        track_id        = "track_id"
        artist_id       = "artist_id"
        album_id        = "album_id"
        track_name      = "track_name"
        artist_name     = "artist_name"
        album_name      = "album_name"
        date            = "date"
        album_release   = "album_release_date"
        album_tracks    = "album_total_tracks"
        duration        = "track_duration"
        explicit        = "explicit"
        popularity      = "track_popularity"
    
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
    #Define the payload we will use
    payload = {
        "api_key":  func_dict.api_key,
        "method":   func_dict.method,
        "format":   func_dict.json,
        "limit":    200,
        "user":     user_name,
        "extended": 1,
        "page":     page
    }

    #Use requests to send the payload to the root URL as a JSON.
    r = requests.get(func_dict.api_root_url, headers=headers, params=payload)
    retrieved_json = r.json()
    
    #Retrieve the attributes from the JSON using the proper keys.
    attributes = retrieved_json[func_dict.root_key][func_dict.attributes]

    #Generate an error if the requested page exceeds the number of total pages returned
    if page > int(attributes['totalPages']):
        raise ValueError("Exceeded total number of pages")
    
    #Return the tracks value from the JSON for processing.
    return retrieved_json[func_dict.root_key][func_dict.tracks]

def parse_page(page_data):
    
    #This temporary list functions to store a list of dictionaries that will then be converted into a DataFrame
    temp_list = []

    #For each entry in the input data, which should be the direct output from the retrieve_page function, add a new item
    #to the list
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
    
    #Once we're done iterating over the input data, turn it into a dataframe, parse the time column into a pandas datetime
    #given that it is given back as seconds in Unix time, then return the resulting dataframe
    return_df = pd.DataFrame(temp_list)
    return_df[func_dict.df_columns.date] = pd.to_datetime(return_df[func_dict.df_columns.date], unit="s")
    return return_df

# %%

def retrieve_all_played_tracks(user_name):

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

    #Sets up a list that will hold the resulting DataFrame from the parse_page function. We will concatenate them all
    #together at the end.
    list_of_dataframes = []

    #Use the retrieved total_pages from the attributes to iterate over each. Can be optimized to not retrieve the first
    #page again, but for brevity of the gist this will just re-request the first page.
    for i in range(total_pages):
        #\r at the beginning is solely for compatibility with VSCode's Python Interactive
        print(f"\rPage {i + 1} of {total_pages}", end="")
        time_start = time.time()
        
        #This will loop on a KeyError since that means we received an empty JSON. This will make it try to retrieve the 
        #failed page again, functionally eliminating the possibility of skipped pages.
        while True:
            try:
                page_data = retrieve_page(user_name, i + 1)
                #If the function gets to this point, break out of the loop and continue
                break
            except KeyError:
                continue
        
        #Parse the page and append it to the list of dataframes, then note how much time was taken for the request to be
        #completed
        list_of_dataframes.append(parse_page(page_data))
        time_taken = time.time() - time_start

        #Debounce the requests to have a maximum of 4 functions per second. This value can be edited to work faster at
        #a heavy risk of getting your API key or IP banned.
        if time_taken < 0.25:
            time.sleep(0.25 - time_taken)
        else:
            continue
    
    #Once all pages have been retrieved, concatenate all the dataframes in the list of dataframes and drop their indices
    #to create a new index. Due to the way the data is formatted and the order of retrieval, this will already be set up
    #time-ascending order, with the first song chronologically at index 0.
    return pd.concat(list_of_dataframes, ignore_index=True)

# %%
df = pd.read_hdf("listener_df.h5", key="df", parse_dates="date")
# %%
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

auth_manager = SpotifyClientCredentials(client_id=spotify_key, client_secret=spotify_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


# %%
def parse_tracks(json):
    new_dict = {
        func_dict.df_columns.album_name:    json[func_dict.album][func_dict.name],
        func_dict.df_columns.album_id:      json[func_dict.album][func_dict.idd],
        func_dict.df_columns.album_release: json[func_dict.album][func_dict.release_date],
        func_dict.df_columns.album_tracks:  json[func_dict.album][func_dict.total_tracks],
        func_dict.df_columns.artist_name:   json[func_dict.artists][0][func_dict.name],
        func_dict.df_columns.artist_id:     json[func_dict.artists][0][func_dict.idd],
        func_dict.df_columns.duration:      json[func_dict.duration],
        func_dict.df_columns.track_name:    json[func_dict.name],
        func_dict.df_columns.track_id:      json[func_dict.idd],
        func_dict.df_columns.explicit:      json[func_dict.explicit],
        func_dict.df_columns.popularity:    json[func_dict.popularity]
    }
    return new_dict

def parse_features(json):
    new_dict = {
        func_dict.idd:                          json[func_dict.idd],
        func_dict.danceability:                 json[func_dict.danceability],
        func_dict.energy:                       json[func_dict.energy],
        func_dict.key:                          json[func_dict.key],
        func_dict.loudness:                     json[func_dict.loudness],
        func_dict.mode:                         json[func_dict.mode],
        func_dict.speechiness:                  json[func_dict.speechiness],
        func_dict.instrumentalness:             json[func_dict.instrumentalness],
        func_dict.acousticness:                 json[func_dict.acousticness],
        func_dict.liveness:                     json[func_dict.liveness],
        func_dict.valence:                      json[func_dict.valence],
        func_dict.tempo:                        json[func_dict.tempo],
        func_dict.time_signature:               json[func_dict.time_signature]
    }
    return new_dict

def parse_multiple_features(response_list):
    return_list = []
    
    for track in response_list:
        try:
            return_list.append(parse_features(track))
        except TypeError:
            continue
    
    return pd.DataFrame(return_list)

def parse_multiple_tracks(response_json):
    list_of_tracks = response_json['tracks']
    return_list = []

    for track in list_of_tracks:
        try:
            return_list.append(parse_tracks(track))
        except TypeError:
            continue

    return pd.DataFrame(return_list)

def start_building_db(input_df):

    #Calculate the number of iterations to run for, minus one
    iterations = math.ceil(len(input_df) / 50) - 1
    #Create an empty list that will contain all the dataframes for each iteration called
    dfs = []

    for i in range(iterations):
        #Slice the list of IDs that will be used. This ensures it will only ever be 50 at a time
        id_list = input_df['track_id'][50 * i : 50 * (i + 1)]
        #retrieve the track JSON for the given list of IDs
        try:
            track_json = sp.tracks(id_list)
        except SpotifyException as e:
            #Retrieve the sleep timer from the 'Retry-After' value in the header, sleep for that amount of time, then
            #try again
            sleep_timer = e.headers['Retry-After']
            time.sleep(sleep_timer)
            track_json = sp.tracks(id_list)
        
        #Parse the resulting JSON
        track_df = parse_multiple_tracks(track_json)

        #Do the exact same but for features
        try:
            feature_json = sp.audio_features(id_list)
        except SpotifyException as e:
            sleep_timer = e.headers['Retry-After']
            time.sleep(sleep_timer)
            feature_json = sp.audio_features(id_list)

        feature_df = parse_multiple_features(feature_json)

        #Merge the two dataframes, using an inner merge to kick out any tracks which would have incomplete information
        merged_df = track_df.merge(feature_df, how="inner", left_on="track_id", right_on="id")

        dfs.append(merged_df)
    
    #Repeat the above process but for the final tracks, which can be up to 50. NOTE: THIS WILL CREATE DUPLICATES. THAT IS FINE
    final_tracks = input_df['track_id'][-50:]
    try:
        return_json = sp.tracks(final_tracks)
    except SpotifyException as e:
        sleep_timer = e.headers['Retry-After']
        time.sleep(sleep_timer)
        return_json = sp.tracks(final_tracks)

    track_df = parse_multiple_tracks(return_json)

    try:
        feature_json = sp.audio_features(final_tracks)
    except SpotifyException as e:
        sleep_timer = e.headers['Retry-After']
        time.sleep(sleep_timer)
        feature_json = sp.audio_features(final_tracks)

    feature_df = parse_multiple_features(feature_json)

    merged_df = track_df.merge(feature_df, how="inner", left_on="track_id", right_on="id")
    dfs.append(merged_df)

    #Concatenate all the dataframes, ignore the index, and drop duplicates created in the last step
    return pd.concat(dfs, ignore_index=True).drop_duplicates(keep="first").reset_index(drop=True)

def search_missing_songs(input_df):

    li = []
    for idx, (track_name, artist_name) in input_df.iterrows():
        try:
            track = sp.search(f"{track_name} artist:{artist_name}")['tracks']['items'][0]
        except IndexError:
            continue
        except SpotifyException as e:
            sleep_timer = e.headers['Retry-After']
            time.sleep(sleep_timer)
            track = sp.search(f"{track_name} artist:{artist_name}")['tracks']['items'][0]

        parsed_track = parse_tracks(track)
        parsed_track['track_select'] =  track_name
        parsed_track['artist_select'] = artist_name
        li.append(parsed_track)
    
    return pd.DataFrame(li)


# %%
full_last_fm = pd.read_hdf("last_fm_no_nans.h5", key="df")
full_last_fm['date'] = pd.to_datetime(full_last_fm['date'])
full_last_fm['end_date'] = full_last_fm['date'] + pd.to_timedelta(full_last_fm['track_duration'].astype(float), unit="ms")
zero_time_delta = pd.Timedelta(0)


 # %%
last_fm_df = pd.read_hdf("appended_lastfm.h5", key="df")
spotify_df = pd.read_hdf("full_spotify_df.h5", key="df")

# %%
import scipy.stats as st

st.expon