# %%
import pandas as pd
import csv
import re

# %%
with open("family_tree.txt") as infile:
    header_skipped = False
    tree = {}
    for line in infile:
        if header_skipped == False:
            if len(re.findall(r"\d+", line)) == 0:
                continue
            else:
                header_skipped = True
                continue
        
        

        

    #Skip rows until you reach the geneology
    while len(re.findall(r"\d+", line)) == 0:
        line = next(infile)
    
    

    

# %%
