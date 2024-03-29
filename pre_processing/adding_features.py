import re
import pandas as pd

data_map = {
    "hockey"    : "../data/hockey_1_text_processed.csv",
    "valentine" : "../data/valentine_1_text_processed.csv",
    "silvester" : "../data/silvester_1_text_processed.csv"
}

name = "hockey"
# 1. Add `total_orders_category_id_X` feature (X = 1.0 ... 6.0)
data = pd.read_csv(data_map[name])

# add one-hot-encoding for category ids
data.title = data.title.apply(lambda x: str(x))
data = pd.concat([data, pd.get_dummies(data["category_id"], prefix="category_id")], axis=1)

# add count for no. of orders for that item (based on item_qty)
# count total of orders per category id
category_ids = [float(i) for i in range(1, 7)]
for category_id in category_ids:
    data["count_category_id_" + str(category_id)] =\
        data["category_id_" + str(category_id)] * data["item_qty"] * (data["sales_before_tax"] > 0)
    
    data["total_orders_category_id_" + str(category_id)] =\
        data.groupby("order_id")["count_category_id_" + str(category_id)].transform("sum")

# drop the one-hot-encoding
one_hot_encoded = ["category_id_" + str(category_id) for category_id in category_ids]
data.drop(one_hot_encoded, axis=1, inplace=True)
# drop the count
count_categories = ["count_category_id_" + str(category_id) for category_id in category_ids]
data.drop(count_categories, axis=1, inplace=True)

# count total sales for table
data['total_sales_before_tax'] = data.groupby('order_id')['sales_before_tax'].transform('sum')
data['total_sales_inc_tax']    = data.groupby('order_id')['sales_inc_tax'].transform('sum')


# 2. Add `total_orders` feature (excluding category 5)
total_categories_ids        = ["total_orders_category_id_" + str(float(i)) for i in range(1, 7)]
total_categories_ids_to_sum = [column for column in total_categories_ids if column != "total_orders_category_id_5.0"]
data["total_orders"]        = data.apply(lambda order: sum(order[column] for column in total_categories_ids_to_sum), axis=1)


# Add order item and table "hour" and "minute" features
data["order_item_time"]   = pd.to_datetime(data["order_item_time"], format="%Y-%m-%d %H:%M:%S.%f")
data["order_time"]        = pd.to_datetime(data["order_time"], format="%Y-%m-%d %H:%M:%S.%f")
data["order_time_closed"] = pd.to_datetime(data["order_time_closed"], format="%Y-%m-%d %H:%M:%S.%f")

#  Add `order_day_of_week` feature
data["order_day_of_week"] = data.order_time.apply(lambda ticket: ticket.day_name())


# 3. Add `is_weekend` feature
weekend = ["Friday", "Saturday", "Sunday"]
data["is_weekend"] = data.order_day_of_week.apply(lambda ticket_day: ticket_day in weekend)


# 4. Add sharable foods
sharable_foods = [
    "pizza", "cake", "hot pot", "nachos", "guac", "wings", "Focaccia", "bread", "fries", "pretzels",
    "quesadilla", "nuts", "fondue", "calamari", "fingers sauced", "chicken fingers", "chkn fingers", "quesa stack" 
]

def find_sharable(title):
    title = " ".join(title.lower().split("."))
    for s in sharable_foods:
        if s in title:
            return 1
    return 0

data["sharable"] = data.title.apply(lambda x: find_sharable(x))


# 5. meal with kids
kids_pattern = re.compile(r'.*kid|k\-|k\.|k ')
data["kids_meal"] = data.title.str.lower().str.match(kids_pattern, na=False).astype(int)


# 6. birthday
data["birthday"] = data.title.apply(lambda x: 1 if 'birthday' in x else 0)


# 7. Adding time type features

# Add `period_of_day` feature ('breakfast', 'lunch', 'afternoon', 'dinner', 'night')
data["order_hour"] = data.order_time.apply(lambda ticket: ticket.hour)

def period_of_day(hour):
    if hour >= 6 and hour < 11    : return 'breakfast'
    elif hour >= 11 and hour < 14 : return 'lunch'
    elif hour >= 14 and hour < 18 : return 'afternoon'
    elif hour >= 18 and hour < 21 : return 'dinner'
    elif hour >= 21 and hour < 23 : return 'hang_out'
    elif hour >= 23 or hour < 6   : return 'night'

data["period_of_day"]      = data.apply(lambda order: period_of_day(int(order["order_hour"])), axis=1)

data["order_minute"]       = data.order_time.apply(lambda ticket: ticket.minute)
data["order_item_minute"]  = data.order_item_time.apply(lambda ticket: ticket.minute)
data["order_item_hour"]    = data.order_item_time.apply(lambda ticket: ticket.hour)
data["order_close_minute"] = data.order_time_closed.apply(lambda ticket: ticket.minute)
data["order_close_hour"]   = data.order_time_closed.apply(lambda ticket: ticket.hour)


import math

def find_total_time(data):
    order_ids = list(data.order_id.value_counts().keys())
    total_dict = {}
    
    for order in order_ids:
        total_dict[order] = {}
        df_order = data[data.order_id == order]

        closing_time = list(df_order.order_time_closed)[0]
        item_times = list(df_order.order_item_time.sort_values())
        earliest_ordering_time = item_times[0]
        order_time = list(df_order.order_time)[0]
        
        if order_time < earliest_ordering_time: 
            total_time = closing_time - order_time
            earliest_time = order_time
        else: 
            total_time = closing_time - earliest_ordering_time
            earliest_time = earliest_ordering_time

        total_dict[order]["total_time"] = total_time / pd.Timedelta('1 hour')

        #Calculating mealflow
        prev = 0
        prev_step = 0
        prev_meal_flow_step = 0
        total_dict[order]["meal_step"] = {}
        total_dict[order]["meal_flow"] = {}
        total_steps = 0
        for i,item in enumerate(item_times):
            #calculating meal step (if there are four orders all at the same time, they will be given 0 - 3 steps. If
            # all the orders were ordered at the same time, they will be given the same step: 0)
            
            
            #Calculating meal flow step - each meal flow step is 4 minutes long.
            if prev == 0:
                prev_step = 1
                total_dict[order]["meal_step"][item] = 1
                diff = (item - earliest_time)
                flow_step = math.floor(((diff.components.hours*60) + diff.components.minutes) /4)
                prev_meal_flow_step = flow_step
                total_dict[order]["meal_flow"][item] = flow_step
                total_dict[order]["meal_flow_beginning"] = flow_step
                prev = item
                continue

            if item == prev:
                continue

            
            diff = item - prev
            if ((diff.components.hours*60) + diff.components.minutes) >= 4:
                total_dict[order]["meal_step"][item] = prev_step + 1
                prev_step = prev_step + 1
            else:
                total_dict[order]["meal_step"][item] = prev_step
            
            flow_step = math.floor(((diff.components.hours*60) + diff.components.minutes) /4) + prev_meal_flow_step
            total_dict[order]["meal_flow"][item] = flow_step
            prev_meal_flow_step = flow_step 
            prev = item
        
        diff = closing_time - item_times[-1]
        last_flow_step = math.floor(((diff.components.hours*60) + diff.components.minutes) /4)
        total_steps = last_flow_step + prev_meal_flow_step
        total_dict[order]["meal_flow_last_to_close"] = last_flow_step
        total_dict[order]["total_meal_flow_steps"] = total_steps

     
    return total_dict


def total_meal_steps(df):
    order_ids = list(data.order_id.value_counts().keys())
    total_dict = {}
    for order in order_ids:
        total_dict[order] = {}
        df_order = data[data.order_id == order]
        
        df_order = df_order.sort_values(by="order_item_time")
        last_meal_step = list(df_order.meal_step.sort_values())[-1]
        total_dict[order]['total_meal_steps'] = last_meal_step

        # from sit down to first order
        meal_flows = [(i * 4 + 1) for i in list(df_order.meal_flow_step)]
        
        max_items_per_step = 0
        for i in range(1,last_meal_step + 1):
            step = df_order[df_order.meal_step == i]
            if len(step) > max_items_per_step:
                max_items_per_step = len(step)
                
        total_dict[order]['max_items_per_step'] = max_items_per_step

        total_dict[order]['sit_to_order'] = meal_flows[0]
        total_dict[order]['first_to_second_order'] = 0
        if len(meal_flows) > 1:
            total_dict[order]['first_to_second_order'] = meal_flows[1] - meal_flows[0]

        total_diff_flows = []
        prev_flow = 0
        for flow in meal_flows:
            if flow == prev_flow:
                continue
            total_diff_flows.append(flow - prev_flow)
            prev_flow = flow

        # avg time between orders
        avg_steps = sum(total_diff_flows)/len(total_diff_flows)
        total_dict[order]['avg_time_between_steps'] = avg_steps
        
        large_meals = 0
        large_sharable_meals = 0
        small_meals = 0
        small_sharable_meals = 0
        
        df_meals = df_order[df_order.category_id == 2]
        for index, row in df_meals.iterrows():
            if row.sales_before_tax >= 6:
                large_meals += row.item_qty
                if row.sharable:
                    large_sharable_meals += row.item_qty
            elif row.sales_before_tax > 0:
                small_meals += row.item_qty
                if row.sharable:
                    small_sharable_meals += row.item_qty
        
        total_dict[order]["total_large_meals"] = large_meals
        total_dict[order]["total_small_meals"] = small_meals
        total_dict[order]["total_large_sharable_meals"] = large_sharable_meals
        total_dict[order]["total_small_sharable_meals"] = small_sharable_meals

    return total_dict

 

# 8. Adding the Meal flow steps
total_dict = find_total_time(data)
data["dwell_time"]              = data.order_id.apply(lambda x: total_dict[x]["total_time"])
data["meal_step"]               = data.apply(lambda x: total_dict[x.order_id]["meal_step"][x.order_item_time], axis=1)
data["meal_flow_last_to_close"] = data.apply(lambda x: total_dict[x.order_id]["meal_flow_last_to_close"], axis=1)
data["total_flow_steps"]        = data.order_id.apply(lambda x: total_dict[x]["total_meal_flow_steps"])
data["meal_flow_step"]          = data.apply(lambda x: total_dict[x.order_id]["meal_flow"][x.order_item_time], axis=1)

#Calculating the total, avg time between meals, time from sit down to ordering, and max items per single step
avg_meal_step_dict = total_meal_steps(data)
data['total_meal_steps']       = data.order_id.apply(lambda x: avg_meal_step_dict[x]['total_meal_steps'])
data['first_to_second_order']  = data.order_id.apply(lambda x: avg_meal_step_dict[x]['first_to_second_order'])
data['avg_time_between_steps'] = data.order_id.apply(lambda x: avg_meal_step_dict[x]['avg_time_between_steps'])
data['sit_to_order']           = data.order_id.apply(lambda x: avg_meal_step_dict[x]['sit_to_order'])
data['max_items_per_step']     = data.order_id.apply(lambda x: avg_meal_step_dict[x]['max_items_per_step'])

#How many small and large meals per table
data['total_large_meals']          = data.order_id.apply(lambda x: avg_meal_step_dict[x]['total_large_meals'])
data['total_small_meals']          = data.order_id.apply(lambda x: avg_meal_step_dict[x]['total_small_meals'])
data['total_large_sharable_meals'] = data.order_id.apply(lambda x: avg_meal_step_dict[x]['total_large_sharable_meals'])
data['total_small_sharable_meals'] = data.order_id.apply(lambda x: avg_meal_step_dict[x]['total_small_sharable_meals'])



data.to_csv("../data/{}_2_text_processed.csv".format(name), index=False)