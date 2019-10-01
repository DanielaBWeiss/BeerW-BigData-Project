#import occasion_classifier as oc
import pandas as pd

LUNCH = "LUNCH"
DINNER = "DINNER"
DRINKING = "DRINKING"
ROMANTIC_DATE = "ROMANTIC_DATE"
FANCY_DATE = "FANCY_DATE"
MALES_ONLY = "MALES_ONLY"
JUST_EATING = "JUST_EATING"
BIRTHDAY = "BIRTHDAY"
KIDS = "KIDS"
NOT_2 = "NOT_2"
UNK = "UNK"


class Bin2Classifier:
    def __init__(self):
        pass
    
    def classify(self, df):
        '''
        :param data: Data is a pandas Dataframe that contains an order_id and a list of ordered items
        :return: The Occasion label, or unknown.
        '''
    
        self.process_table(df)
        feats = self.get_features(df)
        self.period_of_day(df.order_time.iloc[0])
        
        # handling case where only "lunch" time exists
        if self.not_two(df, feats): return NOT_2
        if self.is_lunch(df, feats): return LUNCH
        if self.is_dinner(df, feats): return DINNER
        if self.is_drinking(df, feats): return DRINKING
        if self.is_kids(df, feats): return KIDS
        if self.is_birthday(df, feats): return BIRTHDAY
        if self.is_males_only(df, feats): return MALES_ONLY
        if self.is_romantic(df, feats): return ROMANTIC_DATE
        if self.is_fancy(df, feats): return FANCY_DATE
        if self.is_just_eating(df, feats): return JUST_EATING
        return UNK

    def not_two(self, df, feats):
        if feats["total_foods"] == 1 and feats["soft_drinks"] <= 1 and feats["total_drinks"] == 0:
            return True  # less than two
        if feats["total_foods"] > 11:
            return True 
            
    def is_lunch(self, df, feats):
        if "lunch" not in df.period_of_day.iloc[0]:
            return False
    
        if feats["total_foods"] == 0:
            return False
    
        if df["total_large_meals"].iloc[0] == 0: #at least one large meal must exist for lunch
            return False
    
        if df.dwell_time.iloc[0] > 2: #if meal lasts longer than 2 hours, we do not call it lunch
            return False
    
        if feats['total_drinks'] <= 1: #at this point we have at least one large meal, and at most one drink
            return True
    
        return False
    
    def is_just_eating(self, df, feats):
        if feats["total_foods"] > 0 and feats['total_drinks'] == 0:
            return True
    
        return False
    
    
    def is_birthday(self, df, feats):
        if df.birthday.iloc[0] == 1:
            return True
    
        return False
    
    
    def is_kids(self, df, feats):
        if df.kids_meal.iloc[0] == 1:
            return True
    
        return False
    
    
    def is_dinner(self, df, feats):
        if "dinner" not in df.period_of_day.iloc[0]:
            return False
    
        if df["total_large_meals"].iloc[0] == 0 or df["total_large_meals"].iloc[0] >= 3: #at least one large meal must exist for lunch
            return False
    
        if df["total_meal_steps"].iloc[0] > 3: #if meal lasts longer than 2 hours, we do not call it lunch
            return False
    
        return True
    
    
    def is_romantic(self, df, feats):
        if feats["total_wine"] > 0 and feats["total_beer_volume"] >= 0 and df.dwell_time.iloc[0] > 1:
            return True
    
        return False
    
    
    def is_fancy(self, df, feats):
        if df.total_sales_inc_tax.iloc[0] > 60 and df.dwell_time.iloc[0] > 1:
            return True
    
        return False
    
    
    def is_males_only(self, df, feats):
        if feats["total_wine"] == 0 and feats["total_beer_volume"] > 1 and feats["total_beers"] > 1:
            return True
    
        return False
    
    
    def is_drinking(self, df, feats):
        if feats["total_drinks"] <= 2:
            return False
    
        if feats['total_drinks'] > 2: #at this point we have at least one large meal, and at most one drink
            if feats['total_foods'] == 0 and feats["total_beers"] == 0:
                return True
    
        if feats["total_drinks"] >= 3:
            if feats["total_liquers"] >= 2 and feats["total_foods"] <= 1:
                return True
    
            #if three beers were consumed, they must at least combine to a total of 1.2 liters. (1/3s wont amount to that)
            if feats["total_beer_volume"] >= 1.2 and feats["total_foods"] <= 1:
                return True
    
            # if beers are drank in less than avg 20 minutes between each beer
            if df["avg_time_between_steps"].iloc[0] < 20 and feats["total_foods"] <= 1:
                return True
    
        #Occasion drinking must have at least a ratio of 3:1 for drinks:meals
        if feats['total_foods'] != 0:
            if feats["total_drinks"]/feats['total_foods'] > 1.5:
                return True
        else: 
            return True
    
        return False
    
    def process_table(self, df):
    
        #data["period_of_day"] = data["order_time"].apply(lambda x: period_of_day(x))
        self.fix_times(df)
        df["period_of_day"] = df.order_time.apply(lambda x: self.period_of_day(x))

    
    def get_features(self, df):
        features = {}
    
        features['total_beers'] = df['total_orders_category_id_1.0'].iloc[0]
        features['total_beer_volume'] = df["beer_volume"].iloc[0]
        features['total_liquers'] = df['total_orders_category_id_3.0'].iloc[0] + df['total_orders_category_id_6.0'].iloc[0]
        features['total_wine'] = df['total_orders_category_id_6.0'].iloc[0]
        features['soft_drinks'] = df['total_orders_category_id_4.0'].iloc[0]
        features['total_drinks'] = features['total_beers'] + features['total_liquers']
        features['total_foods'] = df['total_orders_category_id_2.0'].iloc[0]

        return features
    
    
    def fix_times(self, df):
        df['order_time'] = pd.to_datetime(df['order_time'], format="%Y-%m-%d %H:%M:%S.%f")
        df['order_time_closed'] = pd.to_datetime(df['order_time_closed'], format="%Y-%m-%d %H:%M:%S.%f")
        #df['order_item_time'] = pd.to_datetime(df['order_item_time'], format="%Y-%m-%d %H:%M:%S.%f")
    
    def period_of_day(self, order_time):
        hour = order_time.hour
        min = order_time.minute

        time_labels = set()
        if (hour >= 6 and hour < 11):
            time_labels.add('breakfast')
        elif (hour == 10 and min >=50) or (hour >= 11 and hour <= 14):
            time_labels.add('lunch')
        elif (hour >= 14 and hour < 18):
            time_labels.add('afternoon')
        elif (hour >= 18 and hour < 22) or (hour == 17 and min >= 30):
            time_labels.add('dinner')
        elif hour >= 22 or hour <= 4 or (hour == 21 and min >= 45):
            time_labels.add('late_night')
    
        return time_labels


if __name__ == "__main__":
    picked_val_tables = {
        514471619: LUNCH
    }
    df = pd.read_csv("../data/hockey_3_text_processed.csv")

    df = df[df.guest_count == 2].sort_values(by=['order_item_time'])
    df = df[~(df.total_sales_before_tax == 0.)]

    cls = Bin2Classifier()
    results = []
    for k,v in picked_val_tables.items():
        order = df[df.order_id == k]
        order = oc.shrink_orders_to_table(order)
        occasion_labels = cls.classify(order)
        results.append((k,v,occasion_labels))

    df = pd.DataFrame(results, columns=["order_id", "True_label", "Predicted occasion"])
    df.to_csv("cat_2_dev_results.csv", index=False)
    print("Done")