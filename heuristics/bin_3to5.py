FAMILY_EVENT = "FAMILY-EVENT"
DRINKING = "DRINKING"
BREAKFAST = "BREAKFAST"
BRUNCH = "BRUNCH" # currently not in use (until mapping to times of day is done properly)
LUNCH = "LUNCH"
DINNER = "DINNER"
SOCIAL_GATHERING = "SOCIAL-GATHERING"
AFTER_WORK = "AFTER-WORK"
UNK = "UNKNOWN"

class Bin3to5Classifier:
    def __init__(self):
        pass
    
    def _ToD(self, hour):
        if hour >= 6 and hour < 11:
            return BREAKFAST
        elif hour >= 11 and hour <= 14:
            return LUNCH
        elif hour >= 18 and hour < 22:
            return DINNER
        
        return UNK
    
    def _is_after_work(self, day, hour):
        if day in ["Saturday", "Sunday"]:
            return False
        
        if hour >= 15 and hour < 19:
            return True
        return False
    
    def classify(self, table):
        # if table contains "K" as for kids - return FAMILY_EVENT
        if table["kids_meal"]:
            return FAMILY_EVENT

        # else if table contains kids-related items (pancakes, milkshake etc.) - return FAMILY_EVENT
        # TODO: create a list of kids-related items

        # else if table contains mostly alcoholic drinks w/o main dishes - return DRINKING
        if table["total_orders_category_id_3.0"] > 0 and table["total_orders_category_id_2.0"] == 0:
            return DRINKING
        # TODO: figure out WHAT ARE main dishes? (again, create a list / take the whole category_id 2)

        # else if table contains shareable dishes w/ drinks, return:
        # - AFTER_WORK if occurs around after-work hours (15-18) during the weekdays (Monday to Friday)
        # - SOCIAL_GATHERING anytime else
        if table["sharable"]:
            if self._is_after_work(table["order_day_of_week"], table["order_hour"]):
                return AFTER_WORK
            return SOCIAL_GATHERING
        
        # else if table contains mostly main dishes, return according to time of day:
        # - BREAKFAST
        # - BRUNCH
        # - LUNCH
        # - DINNER
        # TODO: use the pre-defined ToD table / generate a new one
        if table["total_orders_category_id_2.0"] >= table["total_orders"] / 2:
            return self._ToD(table.order_hour)
        
        return UNK