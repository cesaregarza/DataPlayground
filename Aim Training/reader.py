# %%
import os, re
import pandas as pd
import numpy as np

path = "F:\\SteamLibrary\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\stats"

# %%
#Create a list of every single csv in the folder
list_of_score_csvs = os.listdir(path)

#Generate a dict of every unique challenge, with the key being the challenge name and the value being the path of every challenge that matches it
regex_challenge_string =    r"[\w\W]+(?=\s\-\sChallenge)"
regex_date_string =         r"\d{4}\.\d{2}\.\d{2}"
regex_date_full_string =    r"\d{4}\.\d{2}\.\d{2}\-\d{2}.\d{2}.\d{2}"


# %%
def parse_csv(input_path):
    #The CSV is set up extremely unusually, so this is to parse it into something usable
    stats_df_cols = ['Weapon', 'Shots', 'Hits', 'Damage Done', 'Damage Possible']
    df =    pd.read_csv(input_path, error_bad_lines=False, warn_bad_lines=False, usecols=list(range(12)))
    date =  re.findall(regex_date_string, input_path)[0]
    
    #Split the top half, the 'data' from the bottom half, the 'stats'. NOTE: THIS RELIES ON SOMEONE NOT TO CHEAT
    data_df =           df.loc[(df['Cheated'].str.lower() == 'false')]
    stats_df =          df.loc[(df['Cheated'].isna())].iloc[:, :5]
    stats_df.columns =  stats_df_cols
    stats_df =          stats_df.set_index("Weapon")

    #TTK is too low resolution for some reason, so we can generate a true TTK by using the high resolution timestamp to calculate a high resolution TTK
    data_df['Timestamp_True'] = pd.to_datetime(date + " " + data_df['Timestamp'])
    data_df['TTK_True'] =       data_df['Timestamp_True'] - data_df['Timestamp_True'].shift()

    #We omit the first value since the TTK for the first target is incalculable without the start time
    #This will calculate the mean and variance in milliseconds. 
    ttk_values =    data_df['TTK_True'].values.astype(np.int64)[1:]
    mean_ttk =      ttk_values.mean() / 1e6
    var_ttk =       ttk_values.var() / 1e12

    #First line contains the accuracy score for some reason. We'll treat it differently
    first_line =    stats_df.iloc[0]
    
    #Calculate accuracy and obtain the score and date to associate the run
    total_acc =     np.int(first_line.loc["Hits"])/np.int(first_line.loc["Shots"])
    score =         np.float(stats_df.loc["Score:", "Shots"])
    date_output =   data_df['Timestamp_True'].max().dt.floor('s')

    #If there's no date_output, we have a game with an invulnerable target. We instead use regex to obtain the date
    if pd.isnull(date_output):
        date_output = pd.to_datetime(re.findall(regex_date_full_string, input_path)[0], format="%Y.%m.%d-%H.%M.%S")

    return [mean_ttk, var_ttk, total_acc, score, date_output]


# %%
#Iterate through each of the files and create a 2D list, which we will then convert to a DataFrame
running_list = []

for filename in list_of_score_csvs:
    match_string = re.findall(regex_challenge_string, filename)[0]
    try:
        running_list += [[match_string, *parse_csv(f"{path}\\{filename}")]]
    except ZeroDivisionError:
        print(filename)
        continue

df = pd.DataFrame(running_list, columns=["Name", "Mean TTK", "Variance TTK", "Accuracy", "Score", "Date"])

# %%
