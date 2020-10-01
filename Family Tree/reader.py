# %%
import pandas as pd
import numpy as np
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
   
# %%
#Parse file on a per-line basis, then create a dataframe to work on
li = []
with open("family_tree.txt", encoding="utf8") as f:
    for line in f:
        li += [line]

df = pd.DataFrame(data=li, columns=["Raw Data"])

#Identify valid lines, extract generational data, remove any invalid lines
df['Generation'] = df['Raw Data'].str.extract(r"([\d\+\*])")
df = df.loc[~df['Generation'].isna()]


# %%
#Strip whitespace
df['Stripped Data'] =   df['Raw Data'].str.lstrip("12345678 \t\n+").str.rstrip()
df['Name'] =            df['Stripped Data'].str.extract(r"([a-zA-Z\ \.óéáúíñ\*0-9]+)")[0].str.strip()
# %%
#Define a function that will be used to apply to the stripped data
def birth_death_married_parser(inp):
    dic = {"b": "", "d": "", "m": ""}
    write_key = None
    for i,x in enumerate(inp):
        try:
            if write_key is not None and x != ":":
                if x in dic.keys() and inp[i + 1] == ":":
                    write_key = x
                    continue
                else:
                    dic[write_key] += x
                    continue
            if x in dic.keys() and inp[i + 1] == ":":
                write_key = x
                continue
        except (KeyError, IndexError):
            continue
    
    return dic

bdm_df = pd.DataFrame(list(df['Stripped Data'].apply(birth_death_married_parser)), index=df.index)
# %%
#merge with original dataframe
merged_df = df.merge(bdm_df, how="left", left_index=True, right_index=True)
#Get dates for births
merged_df['b_date'] = merged_df['b'].str.extract(r"(\d{1,2}\ [a-z]{3}\ \d{4})").fillna(merged_df['b'].str.extract(r"(\d{4})"))

#Grab spousal information
spouses_series =            merged_df["Stripped Data"].str.extract(r"(\[\d+\].+)")
spouses_series =            spouses_series.loc[~spouses_series[0].isna(), 0].str[:-1]
spouses_series =            spouses_series.str.extract(r"([a-zA-Zóéáúíñ\ \.]+)").iloc[:, 0].str.strip()
spouses_series =            spouses_series.reset_index()
spouses_series["index"] +=  1
# spouses_series =            spouses_series.set_index("index")[0]

def retrieve_index_by_name(name):
    return merged_df.loc[merged_df['Name'] == name].index[0]

spouses_series["Spouse Index"] =    spouses_series.loc[:, 0].apply(retrieve_index_by_name)
spouses_series =                    spouses_series.set_index("index")

merged_df['Spouse'] =                           np.nan
merged_df.loc[spouses_series.index, "Spouse"] = spouses_series["Spouse Index"]

spouse_df =                                 merged_df.loc[(merged_df['Generation'] == "+") & (merged_df['Spouse'].isna())].reset_index()
spouse_df['Spouse'] =                       spouse_df['index'] - 1
spouse_df =                                 spouse_df.set_index("index")
merged_df.loc[spouse_df.index, "Spouse"] =  spouse_df['Spouse']
merged_df =                                 merged_df.loc[merged_df['Generation'] != "*"]

merged_df['b'] = merged_df['b'].str.strip()
merged_df['d'] = merged_df['d'].str.strip()
merged_df['m'] = merged_df['m'].str.strip()


# %%
class Node:
    def __init__(self, parent_node, generation, name, birth, death=None, marriage=None, descendant=True):
        self.parent =           parent_node
        self.name =             name
        self.children_nodes =   []
        self.partner =          []
        self.descendant =       descendant
        self.birth =            birth
        self.death =            death
        self.marriage =         marriage
        self.generation =       generation
    
    def add_partner(self, spouse, first=True):
        self.partner +=     [spouse]
        if first:
            spouse.add_partner(self, first=False)
    
    def add_child(self, child):
        self.children_nodes +=  [child]
    
    def assign_generation(self, generation):
        self.generation = generation

# %%
#Store the family tree as a list of Nodes, then store the current parent as max_depth
family_tree = []
prev_row, max_depth = None, None
max_depth_list = []
merged_df['Node'] = None

for idx, row in merged_df.iterrows():

    if row['Generation'] == "1":
        prev_idx, prev_row = idx, row
        self_node = Node(None, 1, row['Name'], row['b'], row['d'], row['m'])
        family_tree += [self_node]
        max_depth = [1, self_node]
        max_depth_list += [max_depth]
        merged_df.loc[idx, 'Node'] = self_node
        continue
    
    if row['Generation'] == "+":
        self_node =             Node(None, None, row['Name'], row['b'], row['d'], row['m'], descendant=False)
        partner_node =          merged_df.loc[int(row['Spouse']), 'Node']
        self_node.assign_generation(partner_node.generation)

        partner_node.add_partner(self_node)
        family_tree += [self_node]
        merged_df.loc[idx, 'Node'] = self_node
        prev_idx, prev_row = idx, row
        continue
    else:
        gen = int(row['Generation'])
        if (prev_row['Generation'] == "+" and merged_df.loc[prev_idx, 'Node'].generation < gen) or gen > max_depth[0]:
            if gen - 1 > max_depth[0]:
                try:
                    max_depth = [gen - 1, merged_df.loc[prev_idx, 'Node'].partner[0]]
                except IndexError:
                    max_depth = [gen - 1, merged_df.loc[prev_idx, 'Node']]
                
                if gen - 1 > len(max_depth_list):
                    max_depth_list += [max_depth]
                else:
                    max_depth_list[gen - 2] = max_depth
            self_node =     Node(max_depth[1], gen, row['Name'], row['b'], row['d'], row['m'])
            max_depth[1].add_child(self_node)
            family_tree += [self_node]
            merged_df.loc[idx, 'Node'] = self_node
            prev_idx, prev_row = idx, row
            continue
        else:
            max_depth = max_depth_list[gen - 2]
            
            self_node = Node(max_depth[1], gen, row['Name'], row['b'], row['d'], row['m'])
            max_depth[1].add_child(self_node)
            merged_df.loc[idx, 'Node'] = self_node
            prev_idx, prev_row = idx, row
            continue




# %%
