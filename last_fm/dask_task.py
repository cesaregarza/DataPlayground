# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import requests
from last_fm_secrets import *
import time
import numpy as np
import pandas as pd
import math
from plotly import express as px
import seaborn as sns
import dask.dataframe as dd
import dask_ml
import tensorflow as tf
from tqdm import tqdm

import sqlite3
conn = sqlite3.connect('last_fm.db')

pdix = pd.IndexSlice

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
    metrics             = ["danceability",
                           "energy", 
                           "key", 
                           "loudness",
                           "mode",
                           "speechiness",
                           "instrumentalness",
                           "acousticness",
                           "liveness",
                           "valence",
                           "tempo",
                           "time_signature"]

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
        track_merge     = "track_name_merge"
        artist_merge    = "artist_name_merge"
    
    def __init__(self):
        self.df_columns = self.DataFrame_Columns_Class()

func_dict = Function_Dictionary_Class()


headers = {
    "user-agent": func_dict.user_agent
}


# %%
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

auth_manager = SpotifyClientCredentials(client_id=spotify_key, client_secret=spotify_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

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
    list_of_tracks = response_json[func_dict.tracks]
    return_list = []

    for track in list_of_tracks:
        try:
            return_list.append(parse_tracks(track))
        except TypeError:
            continue

    return pd.DataFrame(return_list)

def spotify_call(func):
    """Wrapper for functions that call on the spotify API. Automatically handles SpotifyExceptions

    Args:
        func (function): Any function to be wrapped
    """

    def wrapped_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except SpotifyException as e:
            sleep_timer = e.headers[func_dict.retry_after]
            #0.1 is an arbitrary choice, can be reduced if necessary
            time.sleep(sleep_timer + func_dict.additional_wait)
            result = wrapped_func(*args, **kwargs)
        
        return result
    
    return wrapped_func

@spotify_call
def spotify_next(next_json):
    return sp.next(next_json)

@spotify_call
def spotify_tracks(input_list):
    return sp.tracks(input_list)

@spotify_call
def spotify_audio_features(input_list):
    return sp.audio_features(input_list)

@spotify_call
def retrieve_all_playlists_on_page(playlist_page_df):
    """Generates a pandas dataframe containing every single track on every single playlist

    Args:
        playlist_page_df (pd.DataFrame): DataFrame containing the playlist ID and name as columns

    Returns:
        pd.DataFrame: DataFrame with all the resulting tracks with a genre choice appended
    """
    list_of_dfs = []
    for idx, [current_name, current_id] in playlist_page_df.iterrows():
        #This is a very rudimentary approach to keep only the genre name
        genre_name                          = current_name[len("The Sound of "):]
        playlist_df                         = retrieve_all_tracks_from_playlist(current_id)
        playlist_df[func_dict.genre_name]   = genre_name
        list_of_dfs                        += [playlist_df]
    
    #Concatenate all the resulting tracks
    return pd.concat(list_of_dfs, ignore_index=True)
      
        
def retrieve_all_tracks_from_playlist(playlist_id):
    """Generates a DataFrame with the track ID for every item in the given playlist

    Args:
        playlist_id (str): String containing the playlist ID

    Returns:
        pd.DataFrame: DataFrame containing the track ID for every track in the playlist
    """
    fields = "tracks.items.track.id, tracks.next"
    response_json = sp.playlist(playlist_id, fields=fields)[func_dict.tracks]
    return_df = pd.json_normalize(response_json[func_dict.items])

    while response_json[func_dict.nextt]:
        response_json = spotify_next(response_json)
        return_df = pd.concat([return_df, pd.json_normalize(response_json[func_dict.items])[["track.id"]]], ignore_index=True)
        try:
            response_json[func_dict.nextt]
        except KeyError:
            break
    
    return return_df


def build_training_db():
    """Iterate through the playlists by user "thesoundsofspotify" and retrieve every song with its associated genre

    Returns:
        pd.DataFrame: DataFrame containing the track and audio feature information of each track as well as the genre
    """

    #Basic setup
    user = "thesoundsofspotify"
    base_len = len("The Sound of ")
    response_json = sp.user_playlists(user)
    response_df = pd.json_normalize(response_json[func_dict.items])
    initial_playlist_no = len(response_df)

    #Filter dataframe to only include 'The Sound of'
    response_df = response_df.loc[response_df[func_dict.name].apply(len) > base_len, [func_dict.name, func_dict.idd]]

    return_df   = retrieve_all_playlists_on_page(response_df)
    return_df.to_sql("Training_db", conn, if_exists="append")

    total_playlists = response_json['total']
    progress        = tqdm(total=total_playlists)
    progress.update(initial_playlist_no)

    while response_json[func_dict.nextt]:
        response_json   = spotify_next(response_json)
        response_df     = pd.json_normalize(response_json[func_dict.items])
        no_on_page      = len(response_df)
        response_df     = response_df.loc[response_df[func_dict.name].apply(len) > base_len, [func_dict.name, func_dict.idd]]
        new_df          = retrieve_all_playlists_on_page(response_df)
        new_df.to_sql("Training_db", conn, if_exists="append")

        return_df       = pd.concat([return_df, new_df])
        progress.update(no_on_page)

        try:
            response_json[func_dict.nextt]
        except KeyError:
            break
    
    return return_df


def retrieve_tracks_and_features(input_df):
    """Given an input dataframe with track IDs, retrieve the track information and features

    Args:
        input_df (pd.DataFrame): DataFrame containing a list of track IDs

    Returns:
        pd.DataFrame: DataFrame containing all track information along with audio features
    """

    #Calculate the number of iterations to run for, minus one
    iterations = math.ceil(len(input_df) / 50) - 1
    #Create an empty list that will contain all the dataframes for each iteration called
    dfs = []

    for i in tqdm(range(iterations), total=iterations):
        #Slice the list of IDs that will be used. This ensures it will only ever be 50 at a time
        id_list = input_df[func_dict.df_columns.track_id][50 * i : 50 * (i + 1)]
        #retrieve the track JSON for the given list of IDs

        track_json = spotify_tracks(id_list)
        track_df = parse_multiple_tracks(track_json)

        feature_json = spotify_audio_features(id_list)
        feature_df = parse_multiple_features(feature_json)

        #Merge the two dataframes, using an inner merge to kick out any tracks which would have incomplete information
        merged_df = track_df.merge(feature_df, how="inner", left_on="track_id", right_on="id")

        dfs.append(merged_df)
    
    #Repeat the above process but for the final tracks
    remaining_tracks    = len(input_df) % 50
    final_tracks        = input_df[func_dict.df_columns.track_id][-remaining_tracks:]
    return_json         = spotify_tracks(final_tracks)
    track_df            = parse_multiple_tracks(return_json)

    feature_json        = spotify_audio_features(final_tracks)
    feature_df          = parse_multiple_features(feature_json)

    merged_df           = track_df.merge(feature_df, how="inner", left_on="track_id", right_on="id")
    dfs.append(merged_df)

    #Concatenate all the dataframes, ignore the index, and drop duplicates created in the last step
    return pd.concat(dfs, ignore_index=True).drop_duplicates(keep="first").reset_index(drop=True)


# %%
from dask.distributed import Client
db_path = "sqlite:///last_fm.db"
client = Client(n_workers = 1, threads_per_worker=16, memory_limit="25GB", processes=False)
client
feature_ddf = dd.read_sql_table("FEATURES", db_path, "index", npartitions=10)
genre_track_ddf = dd.read_sql_table("TRAINING_DB_2", db_path, "index", npartitions=10)
genre_track_ddf = genre_track_ddf.loc[~genre_track_ddf['track_id'].isna()].set_index("track_id")


# %%
genre_feature_ddf = feature_ddf.merge(genre_track_ddf, on=func_dict.df_columns.track_id).set_index("track_id")


# %%
from dask_ml.preprocessing import Categorizer, DummyEncoder
from sklearn.pipeline import make_pipeline

pipe = make_pipeline(
    Categorizer(),
    DummyEncoder()
)
pipe.fit(genre_track_ddf)
categorized_ddf = pipe.transform(genre_track_ddf)


# %%
merged_ddf = genre_feature_ddf.merge(categorized_ddf, how="left", left_index=True, right_index=True)


# %%
X_train, X_test, y_train, y_test = dask_ml.model_selection.train_test_split(merged_ddf[func_dict.metrics], merged_ddf[categorized_ddf.columns], test_size=0.2, train_size=0.8)


# %%
def build_model():
    layers = [
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(5543, activation="sigmoid")
    ]
    try:
        model = tf.keras.models.Sequential(layers)
    except TypeError:
        model = build_model()

    model.compile(optimizer="adam", loss=tf.keras.losses.binary_crossentropy, metrics=['accuracy'])
    return model

compmodel = build_model()


# %%
from scikeras.wrappers import KerasClassifier
partial_model = KerasClassifier(build_fn=build_model)
model = dask_ml.wrappers.Incremental(partial_model)


# %%
model.fit(X_train, y_train)