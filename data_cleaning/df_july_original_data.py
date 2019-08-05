'''
Creating the first version of the data we will be working with
This is the entrypoint to using our data in this first version. 
We remove unwanted columns and choose a single city to be our focal point.
Any changes to the data that is common to all the groupmembers, 
will be contained in a notebook and will contain the steps necessary to replicate the data to work with.¶
'''


import numpy as np
import pandas as pd

df = pd.read_csv("../data/original_data.csv")

df.drop("country",axis=1,inplace=True) # only single country, no need
df = df[df["bar_type"]!= "Night Club"] # only 83 rows from Night Club 
df.drop(["data_availability_status_id","is_bulk","status","last_status","state","state_id","waiter_id","country_id"],axis=1,inplace=True) # only single country, no need
df = df[df["city"] == "Toronto"] #choose only Toronto city
df.to_csv("df_july.csv", index=False)