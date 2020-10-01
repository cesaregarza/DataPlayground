# %%
import pandas as pd
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
df['Name'] =            df['Stripped Data'].str.extract(r"([a-zA-Z\ \.óé\*1-4]+)")[0].str.strip()
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
# %%
class Node:
    def __init__(self, parent_node, name, birth, death=None, marriage=None, descendant=True):
        self.parent =           parent_node
        self.name =             name
        self.children_nodes =   []
        self.partner =          []
        self.descendant =       descendant
        self.birth =            birth
        self.death =            death
        self.marriage =         marriage
    
    def add_partner(self, spouse):
        self.partner +=     [spouse]
        spouse.partner +=   [self]
    
    def add_child(self, child):
        self.children_nodes +=  [child]

# %%
#Store the family tree as a list of Nodes, then store the current parent as max_depth
family_tree = []
prev_row, max_depth = None, None

for idx, row in merged_df.iterrows():
    if row['Generation'] == "1":
        prev_idx, prev_row = idx, row
        self_node = Node(None, row['Name'], row['b'], row['d'], row['m'])
        family_tree += [self_node]
        max_depth = [1, self_node]
        continue
    
    if row['Generation'] == "+":
        self_node =     Node(None, row['name'], row['b'], row['d'], row['m'], descendant=False)
        partner_node =  family_tree[-1]
        partner_node.add_partner(self_node)
        prev_idx, prev_row = idx, row
        continue
    else:
        gen = int(row['Generation'])
        if prev_row['Generation'] == "+" or gen >= max_depth[0]:
            self_node =     Node(max_depth[1], row['Name'], row['b'], row['d'], row['m'])
            max_depth[1].add_child(self_node)
            prev_idx, prev_row = idx, row
            continue
        else:
            while gen < max_depth[0]:
                max_depth = [max_depth[0] - 1, max_depth[1].parent]



# %%
