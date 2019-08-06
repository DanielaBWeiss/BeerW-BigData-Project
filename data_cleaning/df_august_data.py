import pandas as pd
import numpy as np

table_path = "../data/df_july.csv"

df = pd.read_csv(table_path)
data = df.copy()

data["total_orders"] = data.groupby("order_id")["order_id"].transform("size")

data = pd.concat([data, pd.get_dummies(data["category_id"], prefix="category_id")], axis=1)


category_ids = [float(i) for i in range(1, 7)]
for category_id in category_ids:
    data["total_orders_category_id_" + str(category_id)] =\
        data.groupby("order_id")["category_id_" + str(category_id)].transform("sum")


one_hot_encoded = ["category_id_" + str(category_id) for category_id in category_ids]
data.drop(one_hot_encoded, axis=1, inplace=True)


data.to_csv("../data/df_august.csv", index=False)