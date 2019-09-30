FAMILY_EVENT = "FAMILY_EVENT"
DRINKING = "DRINKING"
BREAKFAST = "BREAKFAST"
LUNCH = "LUNCH"
DINNER = "DINNER"
SOCIAL_GATHERING = "SOCIAL_GATHERING"
AFTER_WORK = "AFTER_WORK"
UNK = "UNKNOWN"


class Bin3to5Classifier:
    def __init__(self):
        pass
    
    def _ToD(self, hour):
        if hour >= 6 and hour < 11:
            return BREAKFAST
        elif hour >= 11 and hour <= 14:
            return LUNCH
        elif hour >= 16 and hour <= 22:
            return DINNER
        
        return UNK
    
    def _is_after_work(self, day, hour):
        if day in ["Saturday", "Sunday"]:
            return False
        if hour >= 15 and hour < 19:
            return True
        return False
    
    def classify(self, table):
        if table["kids_meal"].iloc[0]:
            return FAMILY_EVENT

        if table["total_orders_category_id_3.0"].iloc[0] > 0 and table["total_orders_category_id_2.0"].iloc[0] == 0:
            return DRINKING
        
        if table["sharable"].iloc[0] and \
                (table["total_large_meals"].iloc[0] - table["total_large_sharable_meals"].iloc[0]) < (table["guest_count"].iloc[0] - 1):
            if self._is_after_work(table["order_day_of_week"].iloc[0], table["order_hour"].iloc[0]):
                return AFTER_WORK
            return SOCIAL_GATHERING
        
        if table["total_orders_category_id_2.0"].iloc[0] >= (table["guest_count"].iloc[0] / 2):
            return self._ToD(table["order_hour"].iloc[0])
        
        return UNK