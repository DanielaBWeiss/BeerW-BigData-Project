import pandas as pd

data_map = {
    "hockey"    : "../data/hockey_3_text_processed.csv",
    "valentine" : "../data/valentine_3_text_processed.csv",
    "silvester" : "../data/silvester_3_text_processed.csv"
}

name = "hockey"
data = pd.read_csv(data_map[name])


def shrink_orders_to_tables(data):
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
    
    return data

data = shrink_orders_to_tables(data)


data.to_csv("../data/{}_processed_tables.csv".format(name), index=False)