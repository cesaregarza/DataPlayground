# %%
import os, gzip, json
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

# %%
class Function_Dictionary_Class():
    base_path       = "F:\\Dev\\DataPlayground\\Slay_The_Spire\\Monthly_2020_11\\"
    play_id         = "play_id"
    floor           = "floor"
    card_choices    = "card_choices"
    not_picked      = "not_picked"
    picked          = "picked"
    event_choices   = "event_choices"
    player_choice   = "player_choice"
    damage_taken    = "damage_taken"
    relics_obtained = "relics_obtained"
    potions_obtained= "potions_obtained"
    new_relic       = "new_relic"
    new_potion      = "new_potion"


    columns_full_floors = ["gold_per_floor",
                           "path_per_floor",
                           "current_hp_per_floor",
                           "max_hp_per_floor"]

func_dict = Function_Dictionary_Class()

def drop_json_duplicates_simple(json_list):
    #Create a list that will contain all the objects we've seen so far
    existing_objects = []
    
    #Iterate through each item in json_list. If it hasn't been seen before, add it to our existing objects list. 
    #Otherwise, continue
    for item in json_list:
        if item not in existing_objects:
            existing_objects += [item]
    
    return existing_objects

def drop_json_duplicates(json_list, column_key, replace_key = None):
    #Create a list that will contain all the objects we've seen so far, and one of all the floors we've seen so far
    existing_objects, existing_floors = [], []

    #Iterate through each item in json_list
    for item in json_list:
        #If the item already exists, just continue
        if item in existing_objects:
            continue
        #If the item does not exist but the floor already previously exists
        elif item[func_dict.floor] in existing_floors:

            #The following logic is to designate how to handle when the fed json has a generic name we want to rename to
            #something else
            #If the replace key was designated
            if replace_key is not None:
                #We use try here because jsons will not have a NaN value for missing columns, it just won't include the 
                #key-value pair at all.
                try:
                    #Replace the key at the replace_key with the column_key
                    existing_objects[-1][column_key] = existing_objects[-1].pop(replace_key)
                except KeyError:
                    pass
            else:
                #If the replace key was not designated, just use the column key instead
                replace_key = column_key

            #Find the keys of the previously existing object with the same floor
            previous_keys       = existing_objects[-1].keys()
            #Find and list all keys in the previous item that contain the column key somewhere
            previous_choices    = [key for key in previous_keys if column_key in key]

            #Create a new key-value pair with a number one greater than the previous value with the same column key
            #For example: player_choice becomes player_choice.2 for the first subsequent choice on the same floor, and 
            #player_choice.3 on the next one, etc.
            existing_objects[-1][f"{column_key}.{len(previous_choices) + 1}"] = item[replace_key]
            continue
        #If the item does not exist and the floor does not previously exist
        else:
            #If the replace key was designated, replace it in the json before appending the dict to existing_objects
            if replace_key is not None:
                try:
                    item[column_key] = item.pop(replace_key)
                except KeyError:
                    pass
            
            #Add the item to the existing object list, as well as the existing floor list
            existing_objects += [item]
            existing_floors  += [item[func_dict.floor]]
        
    return existing_objects


def parse_file(path):

    #Use gzip to open the json file at the path provided and parse it
    with gzip.open(path, "r") as f:
        data        = f.read()
        raw_json    = json.loads(data.decode('utf-8'))
    
    #Use json normalize on the extracted raw json, then use convert_dtypes to automatically convert the appropriate 
    #columns into their appropriate types
    raw_df          = pd.json_normalize(raw_json).convert_dtypes()
    #Remove the prefixed "event" from each column
    raw_df.columns  = [col[6:] for col in raw_df.columns]
    raw_df          = raw_df.set_index[func_dict.play_id]

    floors_df = generate_floor_dataframe(raw_df)

    #Currently certain duplicates that survived the dedupe process cause issues. Drop them for now.
    duplicated_indices  = floors_df.index.duplicated().unique(level=0)
    #Remove them from the floors dataframe
    floors_df           = floors_df.loc[~floors_df.index.isin(duplicated_indices, level=0)]
    

def generate_floor_dataframe(raw_df):

    #The columns found at func_dict.columns_full_floors are lists that correspond to each "floor" and pseudo-floor the 
    #user reaches. This will go through each column, turn the list into a series, and stack them to create a new dataframe
    floors_df       = raw_df[func_dict.columns_full_floors].apply(lambda x: x.apply(pd.Series).stack())
    floors_df.index = floors_df.index.rename([func_dict.play_id, func_dict.floor])

    #To append other information from json, an iterative approach is preferred.
    list_of_dfs     = []
    for index, row in tqdm(raw_df.iterrows(), total=len(raw_df)):
        #Card Choices
        temporary_json          = drop_json_duplicates_simple(row[func_dict.card_choices])
        temporary_df_1          = pd.json_normalize(temporary_json)

        #Event Choices
        temporary_json          = drop_json_duplicates(row[func_dict.event_choices], func_dict.player_choice)
        temporary_df_2          = pd.json_normalize(temporary_json)

        #Damage Taken
        temporary_json          = drop_json_duplicates(row[func_dict.damage_taken], "damage")
        temporary_df_3          = pd.json_normalize(temporary_json)

        #Relics Obtained
        temporary_json          = drop_json_duplicates(row[func_dict.relics_obtained], func_dict.new_relic, "key")
        temporary_df_4          = pd.json_normalize(temporary_json)

        #Potions Obtained
        temporary_json          = drop_json_duplicates(row[func_dict.potions_obtained], func_dict.new_potion, "key")
        temporary_df_5          = pd.json_normalize(temporary_json)

        list_of_temporary_dfs = [
            temporary_df_2,
            temporary_df_3,
            temporary_df_4,
            temporary_df_5
        ]

        merged_df = temporary_df_1.copy()

        #Iteratively merge each temporary dataframe into the merged one. Use try-except block to handle empty dataframes
        for df in list_of_temporary_dfs:
            try:
                merged_df = merged_df.merge(df, how="outer", on=func_dict.floor)
            except KeyError:
                continue
        
        #Add the index to the merged dataframe as a new column and added to the list of dataframes
        merged_df[func_dict.play_id] = index
        list_of_dfs += [merged_df]
    
    #Concatenate all of the dataframes together and set the multi-level index
    concat_df                   = pd.concat(list_of_dfs)
    concat_df[func_dict.floor]  = concat_df[func_dict.floor].astype(int)
    concat_df                   = concat_df.set_index([func_dict.play_id, func_dict.floor])
    
    #Explode the "not_picked" column into multiple columns instead of a list and name the columns appropriately
    not_picked_df               = concat_df.apply(lambda x: pd.Series(x[func_dict.not_picked]).explode(), result_type="expand", axis=1)
    not_picked_df.columns       = [f"not_picked.{col}" for col in not_picked_df.columns]

    #Merge the new columns into concat_df and drop the old "not_picked" column
    concat_df                   = not_picked_df.merge(concat_df, how="outer", left_index=True, right_index=True)\
                                               .drop(func_dict.not_picked, axis=1)

    #Merge concat_df into floors and return the resulting dataframe
    return floors_df.merge(concat_df, how="left", left_index=True, right_index=True)