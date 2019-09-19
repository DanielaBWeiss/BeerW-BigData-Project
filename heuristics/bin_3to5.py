FAMILY_EVENT = "FAMILY-EVENT"
DRINKING = "DRINKING"
BREAKFAST = "BREAKFAST"
BRUNCH = "BRUNCH"
LUNCH = "LUNCH"
DINNER = "DINNER"
SOCIAL_GATHERING = "SOCIAL-GATHERING"
AFTER_WORK = "AFTER-WORK"

def Bin3to5Classifier(table):
    # if table contains "K" as for kids - return FAMILY_EVENT
    
    # else if table contains kids-related items (pancakes, milkshake etc.) - return FAMILY_EVENT
    # TODO: create a list of kids-related items
    
    # else if table contains mostly alcoholic drinks w/o main dishes - return DRINKING
    # TODO: figure out WHAT ARE main dishes? (again, create a list / take the whole category_id 2)
    
    # else if table contains mostly main dishes, return according to time of day:
    # - BREAKFAST
    # - BRUNCH
    # - LUNCH
    # - DINNER
    # TODO: use the pre-defined ToD table / generate a new one
    
    # else if table contains shareable dishes w/ drinks, return:
    # - AFTER_WORK if occurs around after-work hours (15-18) during the weekdays (Monday to Friday)
    # - SOCIAL_GATHERING anytime else
    