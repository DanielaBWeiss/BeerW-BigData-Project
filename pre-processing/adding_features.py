import pandas as pd

name = "hockey"
# 1. Add `total_orders_category_id_X` feature (X = 1.0 ... 6.0)
data = pd.read_csv("../data/hockey_1_text_processed.csv")

# add one-hot-encoding for category ids
data.title = data.title.apply(lambda x: str(x))
data = pd.concat([data, pd.get_dummies(data["category_id"], prefix="category_id")], axis=1)
# count total of orders per category id
category_ids = [float(i) for i in range(1, 7)]
for category_id in category_ids:
    data["total_orders_category_id_" + str(category_id)] =\
        data.groupby("order_id")["category_id_" + str(category_id)].transform("sum")

# drop the one-hot-encoding
one_hot_encoded = ["category_id_" + str(category_id) for category_id in category_ids]
data.drop(one_hot_encoded, axis=1, inplace=True)



# 2. Add `total_orders` feature (excluding category 5)
total_categories_ids = ["total_orders_category_id_" + str(float(i)) for i in range(1, 7)]
total_categories_ids_to_sum = [column for column in total_categories_ids if column != "total_orders_category_id_5.0"]
data["total_orders"] = data.apply(lambda order: sum(order[column] for column in total_categories_ids_to_sum), axis=1)


# Add order item and table "hour" and "minute" features
data["order_item_time"] = pd.to_datetime(data["order_item_time"], format="%Y-%m-%d %H:%M:%S.%f")
data["order_time"] = pd.to_datetime(data["order_time"], format="%Y-%m-%d %H:%M:%S.%f")
data["order_time_closed"] = pd.to_datetime(data["order_time_closed"], format="%Y-%m-%d %H:%M:%S.%f")

#  Add `order_day_of_week` feature
data["order_day_of_week"] = data.order_time.apply(lambda ticket: ticket.day_name())

# 3. Add `is_weekend` feature
weekend = ["Friday", "Saturday", "Sunday"]
data["is_weekend"] = data.order_day_of_week.apply(lambda ticket_day: ticket_day in weekend)


# 4. Add sharable foods
sharable_foods = [
    "pizza", "cake", "hot pot", "nachos", "guac", "wings", "Focaccia", "bread", "fries", "pretzels",
"quesadilla", "nuts", "fondue", "calamari", "fingers sauced","chicken fingers", "chkn fingers", "quesa stack" 
]

def find_sharable(title):
    title = " ".join(title.lower().split("."))
    for s in sharable_foods:
        if s in title:
            return 1
    return 0

data["sharable"] = data.title.apply(lambda x: find_sharable(x))




# 5. meal with kids
data["kids_meal"] = data.title.apply(lambda x: 1 if 'kid' in x else 0)
# 6. birthday
data["birthday"] = data.title.apply(lambda x: 1 if 'birthday' in x else 0)


# 7. Adding time type features

# Add `period_of_day` feature ('breakfast', 'lunch', 'afternoon', 'dinner', 'night')
data["order_hour"] = data.order_time.apply(lambda ticket: ticket.hour)

def period_of_day(hour):
    if hour >= 6 and hour < 11: return 'breakfast'
    elif hour >= 11 and hour < 14: return 'lunch'
    elif hour >= 14 and hour < 18: return 'afternoon'
    elif hour >= 18 and hour < 21: return 'dinner'
    elif hour >= 21 and hour < 23: return 'hang_out'
    elif hour >= 23 or hour < 6: return 'night'

data["period_of_day"] = data.apply(lambda order: period_of_day(int(order["order_hour"])), axis=1)

data["order_minute"] = data.order_time.apply(lambda ticket: ticket.minute)
data["order_item_minute"] = data.order_item_time.apply(lambda ticket: ticket.minute)
data["order_item_hour"] = data.order_item_time.apply(lambda ticket: ticket.hour)
data["order_close_minute"] = data.order_time_closed.apply(lambda ticket: ticket.minute)
data["order_close_hour"] = data.order_time_closed.apply(lambda ticket: ticket.hour)


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
  
total_dict = find_total_time(data)


# 8. Adding the Meal flow steps
data["dwell_time"] = data.order_id.apply(lambda x: total_dict[x]["total_time"])
data["meal_step"] = data.apply(lambda x: total_dict[x.order_id]["meal_step"][x.order_item_time], axis=1)
data["meal_flow_last_to_close"] = data.apply(lambda x: total_dict[x.order_id]["meal_flow_last_to_close"], axis=1)
data["total_flow_steps"] = data.order_id.apply(lambda x: total_dict[x]["total_meal_flow_steps"])
data["meal_flow_step"] = data.apply(lambda x: total_dict[x.order_id]["meal_flow"][x.order_item_time], axis=1)


data.to_csv("../data/"+name+"_2_text_processed.csv", index=False)