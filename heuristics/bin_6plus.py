FAMILY_EVENT = "FAMILY_EVENT"
DRINKING = "DRINKING"
BREAKFAST = "BREAKFAST"
LUNCH = "LUNCH"
DINNER = "DINNER"
SOCIAL_GATHERING = "SOCIAL_GATHERING"
DRINKING_PARTY = "DRINKING_PARTY"
AFTER_WORK = "AFTER_WORK"
UNK = "UNKNOWN"

class Bin6PlusClassifier:
    def __init__(self):
        pass
    
    def _ToD(self, hour):
        if hour >= 6 and hour < 11:
            return BREAKFAST
        elif hour >= 11 and hour <= 14:
            return LUNCH
        elif hour >= 16 and hour < 23:
            return DINNER
        
        return UNK
    
    def _is_after_work(self, day, hour):
        if day in ["Saturday", "Sunday"]:
            return False
        if hour >= 15 and hour < 19:
            return True
        return False
    
    def sum_of_all_drinks(self,table):
        return table["total_orders_category_id_3.0"].iloc[0] + table["total_orders_category_id_1.0"].iloc[0] + table["total_orders_category_id_4.0"].iloc[0] + table["total_orders_category_id_6.0"].iloc[0]
                                
    
    def classify(self, table):
        # if table contains "K" as for kids - return FAMILY_EVENT
        if table["kids_meal"].iloc[0]:
            return FAMILY_EVENT
        
        if self.sum_of_all_drinks(table) + table["total_orders_category_id_2.0"].iloc[0] < table["guest_count"].iloc[0]:
            return UNK
        
        # else if table contains mostly alcoholic drinks w/o main dishes - return DRINKING
        if table["total_orders_category_id_3.0"].iloc[0] > 0 and table["total_orders_category_id_2.0"].iloc[0] == 0:
            if table["guest_count"].iloc[0] > 10:
                return DRINKING_PARTY
            return DRINKING
        
        #else if number of drinks is five times the number of food then it is drinking
        if table["total_orders_category_id_3.0"].iloc[0] + table["total_orders_category_id_1.0"].iloc[0] > 5 * table["total_orders_category_id_2.0"].iloc[0]:
            if table["guest_count"].iloc[0] > 10:
                return DRINKING_PARTY
            return DRINKING
        

        
        # TODO: figure out WHAT ARE main dishes? (again, create a list / take the whole category_id 2)

        # else if table contains shareable dishes w/ drinks, return:
        # - AFTER_WORK if occurs around after-work hours (15-18) during the weekdays (Monday to Friday)
        # - SOCIAL_GATHERING anytime else
        # if more than 2/3 of the guest order personal dish than it should be calssified as meal
        if table["sharable"].iloc[0] and (table["total_large_meals"].iloc[0] - table["total_large_sharable_meals"].iloc[0]) < 2*(table["guest_count"].iloc[0])//3:
            if self._is_after_work(table["order_day_of_week"].iloc[0], table["order_hour"].iloc[0]):
                return AFTER_WORK
            return SOCIAL_GATHERING
        
        if (table["total_orders_category_id_1.0"].iloc[0] > table["guest_count"].iloc[0]) and (table["total_large_meals"].iloc[0] < (table["guest_count"].iloc[0])/3):
            if self._is_after_work(table["order_day_of_week"].iloc[0], table["order_hour"].iloc[0]):
                return AFTER_WORK
            return SOCIAL_GATHERING
        
        
        # else if table contains mostly main dishes, return according to time of day:
        # - BREAKFAST
        # - BRUNCH
        # - LUNCH
        # - DINNER
        # TODO: use the pre-defined ToD table / generate a new one
        if table["total_orders_category_id_2.0"].iloc[0] > 0.5 * self.sum_of_all_drinks(table):
            meal =  self._ToD(table["order_hour"].iloc[0])
            if table["guest_count"].iloc[0] > 10 and meal != UNK:
                return meal+"_PARTY"
            return meal
        
        if table["total_orders_category_id_2.0"].iloc[0] >= (table["guest_count"].iloc[0] / 2):
            meal = self._ToD(table["order_hour"].iloc[0])
            if table["guest_count"].iloc[0] > 10 and meal != UNK:
                return meal+"_PARTY"
            return meal
        
        return UNK