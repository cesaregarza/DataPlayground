# %%
import os, gzip, json
import pandas as pd
import seaborn as sns
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

# %%
base_path = "F:\\Dev\\DataPlayground\\Slay_The_Spire\\Monthly_2020_11\\"
list_of_paths = os.listdir(base_path)


# %%
path = "F:\\Dev\\DataPlayground\\Slay_The_Spire\\Monthly_2020_11\\2020-11-01-00-07#1067.json.gz"
with gzip.open(path, "r") as f:
    data = f.read()
    xyz = json.loads(data.decode('utf-8'))

sts_df = pd.json_normalize(xyz).convert_dtypes()
sts_df.columns = [col[6:] for col in sts_df.columns]

list_columns = sts_df.select_dtypes(include="object").columns
noli_columns = sts_df.select_dtypes(exclude="object").columns

# %%
sts_df                      = sts_df.set_index(func_dict.play_id)
floors_df                   = sts_df[func_dict.columns_full_floors].apply(lambda x: x.apply(pd.Series).stack())
floors_df.index             = floors_df.index.rename([func_dict.play_id, func_dict.floor])
# %%
li, li_2 = [], []
def drop_json_duplicates(json_list, column_key, replace_key = None):
    existing_objects, existing_floors = [], []
    for item in json_list:
        if item[func_dict.floor] in existing_floors:
            #Identify existing key and generate a new name for it
            if replace_key is not None:
                try:
                    existing_objects[-1][column_key] = existing_objects[-1].pop(replace_key)
                except KeyError:
                    pass
            else:
                replace_key = column_key

            prev_keys = existing_objects[-1].keys()
            previous_choices = [key for key in prev_keys if column_key in key]
            existing_objects[-1][f"{column_key}.{len(previous_choices) + 1}"] = item[replace_key]
            continue
        elif item not in existing_objects:
            if replace_key is not None:
                try:
                    item[column_key] = item.pop(replace_key)
                except KeyError:
                    pass
            
            existing_objects.append(item)
            existing_floors.append(item[func_dict.floor])

    return existing_objects

def drop_json_duplicates_simple(json_list):
    existing_objects = []
    for item in json_list:
        if item not in existing_objects:
            existing_objects.append(item)
    
    return existing_objects

for index, row in tqdm(sts_df.iterrows(), total=len(sts_df)):
    temporary_json                  = drop_json_duplicates_simple(row[func_dict.card_choices])
    temp_ser_1                      = pd.json_normalize(temporary_json)

    temporary_json                  = drop_json_duplicates(row[func_dict.event_choices], func_dict.player_choice)
    temp_ser_2                      = pd.json_normalize(temporary_json)

    temporary_json                  = drop_json_duplicates(row[func_dict.damage_taken], "damage")
    temp_ser_3                      = pd.json_normalize(row[func_dict.damage_taken])

    temporary_json                  = drop_json_duplicates(row[func_dict.relics_obtained], func_dict.new_relic, "key")
    temp_ser_4                      = pd.json_normalize(temporary_json)

    temporary_json                  = drop_json_duplicates(row[func_dict.potions_obtained], func_dict.new_potion, "key")
    temp_ser_5                      = pd.json_normalize(temporary_json)

    try:
        temp_ser_4.columns              = [func_dict.floor, func_dict.new_relic]
    except ValueError:
        pass

    try:
        temp_ser_5.columns              = [func_dict.floor, func_dict.new_potion]
    except ValueError:
        pass


    temp_ser                        = temp_ser_1.copy()
    for test_df in [temp_ser_2, temp_ser_3, temp_ser_4, temp_ser_5]:
        try:
            temp_ser                    = temp_ser.merge(test_df, how="outer", on=func_dict.floor)
        except KeyError:
            continue
    
    temp_ser[func_dict.play_id]     = index
    
    li   += [temp_ser]
    
temp_floors                  = pd.concat(li)
temp_floors[func_dict.floor] = temp_floors[func_dict.floor].astype(int)
temp_floors                  = temp_floors.set_index([func_dict.play_id, func_dict.floor])

not_picked_df                = temp_floors.apply(lambda x: pd.Series(x[func_dict.not_picked]).explode(), result_type="expand", axis=1)
not_picked_df.columns        = [f"not_picked.{col}" for col in not_picked_df]
pick_floors_df               = not_picked_df.merge(temp_floors, how="outer", left_index=True, right_index=True).drop("not_picked", axis=1)
# %%
floors_df = floors_df.merge(pick_floors_df, how="left", left_index=True, right_index=True)

# %%
