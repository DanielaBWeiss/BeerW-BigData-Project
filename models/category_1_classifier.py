import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

LUNCH = "Lunch"

DINNER = "Dinner"

DRINKING = "Drinking"

CASUAL_DRINK_MEAL = "Casual Drink and Meal"

NOT_1 = "Not Category 1"

UNK = "Unknown"

def filter(df):

    for i in range(1,df.total_meal_steps.iloc[0] + 1):
        step = df[df.meal_step == i]
        if len(step) > 3:
            return False

    for meal in list(df.title):
        if "kid" in meal.lower():
            return False

    return True

def fix_times(df):
    df['order_time'] = pd.to_datetime(df['order_time'], format="%Y-%m-%d %H:%M:%S.%f")
    df['order_time_closed'] = pd.to_datetime(df['order_time_closed'], format="%Y-%m-%d %H:%M:%S.%f")
    df['order_item_time'] = pd.to_datetime(df['order_item_time'], format="%Y-%m-%d %H:%M:%S.%f")

def period_of_day(order_time):
    hour = order_time.hour
    min = order_time.minute

    time_labels = set()
    if (hour >= 6 and hour < 11):
        time_labels.add('breakfast')
    elif (hour == 10 and min >=50) or (hour >= 11 and hour <= 2):
        time_labels.add('lunch')
    elif (hour >= 14 and hour < 18):
        time_labels.add('afternoon')
    elif (hour >= 18 and hour < 22) or (hour == 17 and min >= 30):
        time_labels.add('dinner')
    elif hour >= 22 or hour <= 4 or (hour == 21 and min >= 45):
        time_labels.add('late_night')

    return time_labels


def total_meal_steps(df):
    order = {}

    df = df.sort_values(by="order_item_time")
    last_meal_step = list(df.meal_step.sort_values())[-1]
    order['total_meal_steps'] = last_meal_step

    # from sit down to first order
    meal_flows = [(i * 4 + 1) for i in list(df.meal_flow_step)]

    order['sit_to_order'] = meal_flows[0]
    if len(meal_flows) > 1:
        order['first_to_second_order'] = meal_flows[1] - meal_flows[0]

    total_diff_flows = []
    prev_flow = 0
    for flow in meal_flows:
        if flow == prev_flow:
            continue
        total_diff_flows.append(flow - prev_flow)
        prev_flow = flow

    # avg time between orders
    avg_steps = sum(total_diff_flows)/len(total_diff_flows)
    order['avg_time_between_steps'] = avg_steps

    return order

def process_table(df):

    #data["period_of_day"] = data["order_time"].apply(lambda x: period_of_day(x))
    fix_times(df)
    df["period_of_day"] = [period_of_day(df.order_time.iloc[0])]*len(df)
    order_feats = total_meal_steps(df)
    df['total_meal_steps'] = [order_feats['total_meal_steps']]*len(df)
    df['first_to_second_order'] = [order_feats['first_to_second_order']]*len(df)
    df['avg_time_between_steps'] = [order_feats['avg_time_between_steps']] * len(df)

def get_features(df):
    features = {}

    features['total_beers'] = df['total_orders_category_id_1.0'].iloc[0]
    features['total_beer_volume'] = sum(list(df["beer_volume"]))
    features['total_liquers'] = df['total_orders_category_id_3.0'].iloc[0] + df['total_orders_category_id_6.0'].iloc[0]
    features['soft_drinks'] = df['total_orders_category_id_4.0'].iloc[0]
    features['total_drinks'] = features['total_beers'] + features['total_liquers']
    features['total_foods'] = df['total_orders_category_id_2.0'].iloc[0]

    large_meals = 0
    small_meals = 0
    df_meals = df[df.category_id == 2]
    for meal_price in df_meals.sales_before_tax:
        if meal_price >= 6: large_meals += 1
        else: small_meals += 1
    features["total_large_meals"] = large_meals
    features["total_small_meals"] = small_meals

    return features


def is_lunch(df, feats):
    if "lunch" not in df.period_of_day.iloc[0]:
        return False

    if feats["total_foods"] == 0:
        return False

    if feats["total_large_meals"] == 0: #at least one large meal must exist for lunch
        return False

    if feats["dwell_time"] > 2: #if meal lasts longer than 2 hours, we do not call it lunch
        return False

    if feats['total_drinks'] <= 1: #at this point we have at least one large meal, and at most one drink
        return True

    return False

def is_dinner(df, feats):
    if "lunch" in list(df.period_of_day)[0]:
        return False

    if feats["total_large_meals"] == 0 or feats["total_large_meals"] >= 3: #at least one large meal must exist for lunch
        return False

    if df["total_meal_steps"].iloc[0] > 3: #if meal lasts longer than 2 hours, we do not call it lunch
        return False

    return True

def is_drinking(df, feats):
    if feats["total_drinks"] <= 1:
        return False

    if feats['total_drinks'] == 2: #at this point we have at least one large meal, and at most one drink
        if feats['total_foods'] == 0 and feats["total_beers"] == 0:
            return True
        return False

    if feats["total_drinks"] == 3:
        if feats["total_liquers"] >= 2 and feats["total_foods"] <= 1:
            return True

        #if three beers were consumed, they must at least combine to a total of 1.2 liters. (1/3s wont amount to that)
        if feats["total_beer_volume"] >= 1.2 and feats["total_foods"] <= 1:
            return True

        # if beers are drank in less than avg 20 minutes between each beer
        if df["avg_time_between_steps"] < 20 and feats["total_foods"] <= 1:
            return True

    #Occasion drinking must have at least a ratio of 3:1 for drinks:meals
    if feats['total_foods'] != 0:
        if feats["total_drinks"]/feats['total_foods'] > 1.5:
            return True
    else: return True

    return False

def is_casual(df, feats):
    if feats["total_drinks"] == 0:
        return False

    if feats['total_drinks'] == 2: #at this point we have at least one large meal, and at most one drink
        if feats["total_beers"] >= 1:
            return True
        elif feats["total_foods"] >= 1: #if theres only liquer, at least one meal must exist
            return True
        return False

    if feats["total_drinks"] == 3:
        if feats["total_liquers"] <= 1:
            return True

        # if beers are consumed with at least a 20 minutes
        if df["first_to_second_order"] >= 20 or df['sit_to_order'] >= 20:
            return True

    if feats["total_foods"] != 0:
        if feats["total_foods"]/feats["total_drinks"] > 2:
            return False
        return True

    return False

def Bin1Classifier(df):
    '''

    :param data: Data is a pandas Dataframe that contains an order_id and a list of ordered items
    :return: The Occasion label, or unknown.
    '''
    occasion_labels = {"occasion":[], "time":[]}

    process_table(df)
    feats = get_features(df) #get features from dataframe for ease of use
    if not filter(df): #Filter out tables that should not have been labeled with guest count == 1
        occasion_labels["occasion"].append(NOT_1)
        return occasion_labels


    #----HEURISTICS FOR CLASSIFYING OCCASIONS------
    # TODO: more than one large meal
    # TODO: dwell time
    # TODO: meal step time

    #if lunch is one of the time labels, then we can exclude "dinner" occasion, but there could also be "afternoon" time.

    occasion_labels["time"] = df["period_of_day"].iloc[0]

        #handling case where only "lunch" time exists
    if is_lunch(df, feats): occasion_labels["occasion"].append(LUNCH)
    if is_dinner(df, feats): occasion_labels["occasion"].append(DINNER)
    if is_drinking(df, feats): occasion_labels["occasion"].append(DRINKING)
    if is_casual(df, feats): occasion_labels["occasion"].append(CASUAL_DRINK_MEAL)
    if not occasion_labels["occasion"]: occasion_labels["occasion"].append(UNK)
    return occasion_labels



if __name__ == "__main__":
    print("Testing 8 dev labeled order ids")
    picked_hockey_tables = {
        #512690383: CASUAL_DRINK_MEAL,
        #521702519: DRINKING,
        #521093892: DRINKING,
        #517505343: NOT_1,
        #521783372: DINNER,
        #521769692: CASUAL_DRINK_MEAL,
        #512852707: CASUAL_DRINK_MEAL,
        525538989: CASUAL_DRINK_MEAL
    }
    df = pd.read_csv("../data/hockey_3_text_processed.csv")
    df = df[df.guest_count == 1].sort_values(by=['order_item_time'])
    df = df[~(df.total_sales_before_tax == 0.)]

    results = []
    for k,v in picked_hockey_tables.items():
        order = df[df.order_id == k]
        labels = Bin1Classifier(order)
        results.append((k,v,labels))

    df = pd.DataFrame(results, columns=["order_id", "True_label", "Predicted"])
    df.to_csv("cat_1_dev_results.csv", index=False)
    print("Done")