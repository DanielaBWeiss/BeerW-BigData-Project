import numpy as np
import pandas as pd

data_map = {
    "hockey"    : "../data/hockey_2_text_processed.csv",
    "valentine" : "../data/valentine_2_text_processed.csv",
    "silvester" : "../data/silvester_2_text_processed.csv"
}

name = "hockey"
data = pd.read_csv(data_map[name])

data[~(data.guest_count == 0)]


data['total_sales_before_tax'] = data.groupby('order_id')['sales_before_tax'].transform('sum')
data['total_sales_inc_tax']    = data.groupby('order_id')['sales_inc_tax'].transform('sum')
data['total_orders']           = data.groupby('order_id')['order_id'].transform('size')

#columns = ['bar_id', 'order_id', 'order_time', 'order_item_id', 'title', 'category_id',
 #          'beer_volume', 'item_qty', 'guest_count', 'sales_before_tax', 'total_sales_before_tax', 'total_orders']
#data = data[columns]

bars = data.bar_id.unique()

features = ['bar_id', 'guest_count']
tables = data.drop_duplicates(subset='order_id', keep='first')
tables.set_index('order_id', inplace=True)
tables = tables[features]


desc = tables.groupby('bar_id').guest_count.describe()
desc_columns = ['guest_count_count', 'guest_count_mean', 'guest_count_std', 'guest_count_min', \
                'guest_count_25%', 'guest_count_50%', 'guest_count_75%', 'guest_count_max']
desc.columns = desc_columns

tables = tables.reset_index().merge(desc, on='bar_id').set_index(tables.index).drop(['order_id'], axis=1)

bars_data = tables.drop_duplicates(subset='bar_id', keep='first')[['bar_id'] + desc_columns]
bars_data.set_index('bar_id', inplace=True)

assert(len(bars) == len(bars_data))

bars_data = bars_data[(bars_data.guest_count_max != 0) & (bars_data.guest_count_max != 1)]

'''
def filter_sales(row):
    if row["guest_count"] > row["total_sales_before_tax"] and row["total_sales_before_tax"] != 0.0:
        return True
    return False

drops = df[df.apply(lambda x: filter_sales(x), axis=1)]
bad_bars = drops.groupby("bar_id").count()
bad_bars = bad_bars[bad_bars["order_id"] > 20]
bars_data = bars_data[~bars_data.index.isin(list(bad_bars.index))]

bad_data = bars_data[(bars_data["guest_count_75%"] <= 1) | ( bars_data['guest_count_25%'] == 0)]
bars_data2 = bars_data[~bars_data.index.isin(list(bad_data.index))]
best_bars = bars_data2[(bars_data2['guest_count_50%'] >= 1 ) &(bars_data2.guest_count_std <= 1.5)]

last_bars = best_bars[best_bars["guest_count_min"] != 0]
last_bars.to_csv("../data/df_3_text_processed.csv", index=False)
'''

last_bars = bars_data[bars_data["guest_count_min"] != 0]
if len(last_bars) < 25:
    data = data[data.bar_id.isin(bars_data.index)]
else:
    data = data[data.bar_id.isin(last_bars.index)]


data.to_csv("../data/{}_3_text_processed.csv".format(name), index=False)