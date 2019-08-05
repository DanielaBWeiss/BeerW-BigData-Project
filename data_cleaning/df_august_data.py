


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

table_path = "../data/df_july"

df = pd.read_csv(table_path)
data = df.copy()

data["total_orders"] = data.groupby("order_id")["order_id"].transform("size")
data[data["order_id"] == order_id]
data["category_id"].value_counts()
df.category_id.isna().sum()

data = pd.concat([data, pd.get_dummies(data["category_id"], prefix="category_id")], axis=1)
data[data["order_id"] == order_id]

category_ids = [float(i) for i in range(1, 7)]
for category_id in category_ids:
    data["total_orders_category_id_" + str(category_id)] =\
        data.groupby("order_id")["category_id_" + str(category_id)].transform("sum")

 data[data["order_id"] == order_id]

 one_hot_encoded = ["category_id_" + str(category_id) for category_id in category_ids]
data.drop(one_hot_encoded, axis=1, inplace=True)
data[data["order_id"] == order_id]

data.to_csv("df_august.csv")