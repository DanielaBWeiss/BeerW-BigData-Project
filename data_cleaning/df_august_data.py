import pandas as pd

table_path = "../data/df_july_all_cities.csv"

df = pd.read_csv(table_path)
data = df.copy()

data["order_time"] = pd.to_datetime(data["order_time"], format="%Y-%m-%d %H:%M:%S.%f")


# 1. Add `total_orders_category_id_X` feature (X = 1.0 ... 6.0)

# add one-hot-encoding for category ids
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


# 3. Add `day_of_week` feature
data["day_of_week"] = data.order_time.apply(lambda ticket: ticket.day_name())


# 4. Add `period_of_day` feature ('breakfast', 'lunch', 'afternoon', 'dinner', 'night')
data["order_hour"] = data.order_time.apply(lambda ticket: ticket.hour)

def period_of_day(hour):
    if hour >= 6 and hour <= 11: return "breakfast"
    elif hour >= 12 and hour <= 14: return "lunch"
    elif hour >= 13 and hour <= 18: return "afternoon"
    elif hour >= 19 and hour <= 22: return "dinner"
    elif hour >= 23 or hour <= 5: return "night"

data["period_of_day"] = data.apply(lambda order: period_of_day(int(order["order_hour"])), axis=1)
data.drop("order_hour", axis=1, inplace=True)


# 5. Add `is_weekend` feature
weekend = ["Friday", "Saturday", "Sunday"]
data["is_weekend"] = data.day_of_week.apply(lambda ticket_day: ticket_day in weekend)


data.to_csv("../data/df_august.csv", index=False)