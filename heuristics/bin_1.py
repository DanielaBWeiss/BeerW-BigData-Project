import pandas as pd
#import occasion_classifier as oc

pd.options.mode.chained_assignment = None  # default='warn'

LUNCH = "LUNCH"
MUNCH = "MUNCH"
DINNER = "DINNER"
DRINKING = "DRINKING"
CASUAL_DRINK = "CASUAL_DRINK"
NOT_1 = "NOT_1"
UNK = "UNK"



'''
TODO 
- maybe add a category for a late munch/ light meal late at night
- Casual drink and meal could also just be casual drink, therefore either should change the name to casual, or add
  casual drink
- IMPORTANT
    - create an ordering for the labels, maybe doesn't make sense to do multi-label.
- ADD munch


'''

class Bin1Classifier():

    def classify(self, df):
        '''

        :param data: Data is a pandas Dataframe that contains an order_id and a list of ordered items
        :return: The Occasion label, or unknown.
        '''
        self._process_table(df)
        feats = self._get_features(df)

        if not self._filter(df):  # Filter out tables that should not have been labeled with guest count == 1
            return NOT_1


        # ----HEURISTICS FOR CLASSIFYING OCCASIONS------
        # TODO: more than one large meal
        # TODO: dwell time
        # TODO: meal step time

        # if lunch is one of the time labels, then we can exclude "dinner" occasion, but there could also be "afternoon" time.
        time_labels = df["period_of_day"].iloc[0]

        # handling case where only "lunch" time exists
        if self._is_lunch(df, feats): return LUNCH#, time_labels
        if self._is_munch(df, feats): return MUNCH#, time_labels
        if self._is_dinner(df, feats): return DINNER#, time_labels
        if self._is_casual(df, feats): return CASUAL_DRINK#, time_labels
        if self._is_drinking(df, feats): return DRINKING#, time_labels
        return UNK#, []

    def _is_lunch(self, df, feats):
        if "lunch" not in df.period_of_day.iloc[0]:
            return False

        if feats["total_foods"] == 0:
            return False

        if df["total_large_meals"].iloc[0] == 0: #at least one large meal must exist for lunch
            return False

        #if feats["dwell_time"] > 2: #if meal lasts longer than 2 hours, we do not call it lunch
        #    return False

        if feats['total_drinks'] > 1: #at this point we have at least one large meal, and at most one drink
            return False

        return True

    def _is_munch(self, df, feats):
        if "late_night" not in df.period_of_day.iloc[0]:
            return False

        if feats["total_drinks"] == 0 and df["total_sales_before_tax"].iloc[0] <= 15:
            return True

    def _is_dinner(self, df, feats):
        if "dinner" not in df.period_of_day.iloc[0] and "late_night" not in df.period_of_day.iloc[0]:
            return False

        if df["total_large_meals"].iloc[0] == 0: #at least one large meal must exist for lunch
            return False

        if df["total_meal_steps"].iloc[0] > 3: #if meal takes more than three meal steps
            return False

        if feats["total_drinks"] > 2:
            return False

        if feats["total_liquers"] == 2:
            return False

        if (df["total_large_meals"].iloc[0] <= 1 and df["total_large_meals"].iloc[0] > 0) and df["sharable"].iloc[0] == 1 and feats["total_drinks"] > 0:
            return False

        return True

    def _is_drinking(self, df, feats):
        if feats["total_drinks"] <= 1:
            return False

        if feats['total_drinks'] == 2:
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
            if df["avg_time_between_steps"].iloc[0] < 20:
                return True

        #Occasion drinking must have at least a ratio of 3:1 for drinks:meals
        if feats['total_foods'] != 0:
            if feats["total_drinks"]/feats['total_foods'] > 1.5:
                return True
            else: return False
        else:
            return True

        return False

    def _is_casual(self, df, feats):
        if feats["total_drinks"] == 0:
            return False

        if feats["total_drinks"] == 1:
            return True

        if feats['total_drinks'] == 2: #at this point we have at least one large meal, and at most two drink
            if feats["total_beers"] >= 1:
                return True
            elif feats["total_foods"] > 0: #if theres two liquer, at least one meal must exist
                return True
            return False

        if feats["total_drinks"] == 3:
            if feats["total_liquers"] <= 1 and feats["total_foods"] > 0: #This means that we can have either 3 beers or 2 and 1 liquer, but one meal must be there
                return True

            if feats["total_liquers"] >= 2:
                return False

            if feats["total_beer_volume"] < 1.2:
                return True
            # if beers are consumed with at least a 20 minutes
            if df['avg_time_between_steps'].iloc[0] >= 30:
                return True

        if feats["total_foods"] != 0:
            if feats["total_drinks"]/feats['total_foods'] > 1.5:
                return False
            return True

        return False

    def _process_table(self, df):

        #data["period_of_day"] = data["order_time"].apply(lambda x: period_of_day(x))
        self._fix_times(df)
        df["period_of_day"] = df.order_time.apply(lambda x: self._period_of_day(x))
        '''
        order_feats = self.total_meal_steps(df)
        df['total_meal_steps'] = [order_feats['total_meal_steps']]*len(df)
        df['first_to_second_order'] = [order_feats['first_to_second_order']]*len(df)
        df['avg_time_between_steps'] = [order_feats['avg_time_between_steps']] * len(df)
        '''

    def _get_features(self, df):
        features = {}

        features['total_beers'] = df['total_orders_category_id_1.0'].iloc[0]
        features['total_beer_volume'] = df["beer_volume"].iloc[0]
        features['total_liquers'] = df['total_orders_category_id_3.0'].iloc[0] + df['total_orders_category_id_6.0'].iloc[0]
        features['soft_drinks'] = df['total_orders_category_id_4.0'].iloc[0]
        features['total_drinks'] = features['total_beers'] + features['total_liquers']
        features['total_foods'] = df['total_orders_category_id_2.0'].iloc[0]

        '''
        large_meals = 0
        small_meals = 0
        df_meals = df[df.category_id == 2]
        for meal_price in df_meals.sales_before_tax:
            if meal_price >= 6: large_meals += 1
            else: small_meals += 1
        features["total_large_meals"] = large_meals
        features["total_small_meals"] = small_meals
        '''
        return features

    def _filter(self, df):

        if df['max_items_per_step'].iloc[0] > 3:
            return False

        if df["kids_meal"].iloc[0] == 1:
            return False

        return True

    def _fix_times(self, df):
        df['order_time'] = pd.to_datetime(df['order_time'], format="%Y-%m-%d %H:%M:%S.%f")
        df['order_time_closed'] = pd.to_datetime(df['order_time_closed'], format="%Y-%m-%d %H:%M:%S.%f")
        #df['order_item_time'] = pd.to_datetime(df['order_item_time'], format="%Y-%m-%d %H:%M:%S.%f")

    def _period_of_day(self, order_time):
        hour = order_time.hour
        min = order_time.minute

        time_labels = set()
        if (hour >= 6 and hour < 11):
            time_labels.add('breakfast')
        if (hour == 10 and min >=50) or (hour == 14 and min <= 10) or (hour >= 11 and hour <= 13):
            time_labels.add('lunch')
        if (hour >= 14 and hour < 18):
            time_labels.add('afternoon')
        if (hour >= 18 and hour < 22) or (hour == 17 and min >= 30):
            time_labels.add('dinner')
        if hour >= 22 or hour <= 4 or (hour == 21 and min >= 45):
            time_labels.add('late_night')

        return time_labels




if __name__ == "__main__":
    picked_val_tables = {
        514471619: LUNCH
    }
    df = pd.read_csv("../data/hockey_3_text_processed.csv")

    df = df[df.guest_count == 1].sort_values(by=['order_item_time'])
    df = df[~(df.total_sales_before_tax == 0.)]

    cls = Bin1Classifier()
    results = []
    for k,v in picked_val_tables.items():
        order = df[df.order_id == k]
        order = oc.shrink_orders_to_table(order)
        occasion_labels, time_labels = cls.classify(order)
        results.append((k,v,occasion_labels, time_labels))

    df = pd.DataFrame(results, columns=["order_id", "True_label", "Predicted occasion", "time sub-label"])
    df.to_csv("cat_1_dev_results.csv", index=False)
    print("Done")
