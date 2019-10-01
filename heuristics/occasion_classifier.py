import os
import pandas as pd

from bin_1 import Bin1Classifier
from bin_2 import Bin2Classifier
from bin_3to5 import Bin3to5Classifier
from bin_6plus import Bin6PlusClassifier


DATA_PATH = "../data/hockey_3_text_processing.csv" # fix data path

UNK = "UNK"


def add_features(data):
    pass
    #Not sure that this is needed.

def drop_features(data):
    columns = ["bar_id", "order_item_id", "sales_before_tax", "sales_inc_tax", "title",
               "category_id", "beer_brand_id", "beer_serving_type_id",
               "order_item_hour", "order_item_minute", "meal_step", "meal_flow_step"]
    
    data.drop(columns=columns, inplace=True)
    return data


def shrink_orders_to_table(data):
    # use `min` wherever the feature is fixed for the entire table
    # use `max` for booleans (we take the value of True whenever there exists at least 1 truthy order_item of the feature)
    
    data = data.groupby("order_id", as_index=False).agg({
        "order_time": "min",
        "order_time_closed": "min",
        "order_hour": "min",
        "order_minute": "min",
        "order_close_hour": "min",
        "order_close_minute": "min",
        "period_of_day": "min",
        "order_day_of_week": "min",
        "is_weekend": "min",
        
        "item_qty": "sum",
        "beer_volume": "sum",
        "guest_count": "min",
        
        "total_orders_category_id_1.0": "min",
        "total_orders_category_id_2.0": "min",
        "total_orders_category_id_3.0": "min",
        "total_orders_category_id_4.0": "min",
        "total_orders_category_id_5.0": "min",
        "total_orders_category_id_6.0": "min",
        "total_orders": "min",
        "total_large_meals":"min",
        "total_small_meals":"min",
        "total_large_sharable_meals":"min",
        "total_small_sharable_meals":"min",
        
        "sharable": "max",
        "kids_meal": "max",
        "birthday": "max",
        
        "dwell_time": "min",
        "meal_flow_last_to_close": "min",
        "total_flow_steps": "min",
        "total_meal_steps":"min",
        "avg_time_between_steps":"min",
        "sit_to_order":"min",
        "max_items_per_step":"min",
        
        "total_sales_before_tax": "min",
        "total_sales_inc_tax": "min"
    })
    
    data.set_index("order_id", inplace=True)
    return data


def classify(order):
    bin1_classifier = Bin1Classifier()
    bin2_classifier = Bin2Classifier()
    bin3to5_classifier = Bin3to5Classifier()
    bin6plus_classifier = Bin6PlusClassifier()
    
    if order.guest_count.iloc[0] == 1:
        return bin1_classifier.classify(order)
    elif order.guest_count.iloc[0] == 2:
        return bin2_classifier.classify(order)
    elif order.guest_count.iloc[0] >= 3 and order.guest_count.iloc[0] <= 5:
        return bin3to5_classifier.classify(order)
    elif order.guest_count.iloc[0] >= 6:
        return bin6plus_classifier.classify(order)
    else:
        return UNK


def label_data(data, to_csv=False):
    data["pred_occasion"] = data.apply(classify, axis=1)
    
    if to_csv:
        labeled = data[["order_id", "pred_occasion"]]
        output_name = os.path.basename(DATA_PATH) + ".labels.csv"
        labeled.to_csv(output_name)
        print("Created labeled data in {} successfully!".format(output_name))


def main():
    # 0. read data
    data = pd.read_csv(DATA_PATH)
    print("Read data from {}".format(data_path))
    
    # 1. add features to data
    # redundant, we're assuming the `pre-processing/adding_features.py` was used prior to executing this model
#     data = add_features(data)
#     print("Added features")
    data = drop_features(data)
    
    # 2. shrink data to 1 entry (line) per table
    data = shrink_orders_to_table(data)
    print("Created entry per table")
    
    # 3. for each entry, apply the relevant classifier based on the guest_count feature    
    label_data(data, to_csv=True)
    print("Labeling is complete")
    

if __name__ == '__main__':
    main()
    