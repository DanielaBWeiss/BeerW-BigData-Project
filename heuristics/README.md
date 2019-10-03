# Heuristics

As defined earlier, our main goal is to define the consumer mission (ticket mission) - why did the consumer come here?  And a further goal of predicting the Guest Count, based on a table order.
It is a hard problem.

Here, we'll specify the different occasions (there are various of occasions, some specific to certain guest counts).  
There will be 4 different heuristics, one for each bin:
- 1 guest tables
- 2 guests tables
- 3-5 guests tables
- 6+ guests tables

Then, a main script (called `occasion_classifier.py`) will take care of applying the relevant heuristic based on the *guest_count* for each table.
* Make sure to use **all** of the *pre-processing* scripts prior to executing this script.

## Occasions

### Common Occasions to all bins:
BREAKFAST
LUNCH
DINNER
DRINKING
UNKNOWN

### Category 1:
In addition to the common occasions

MUNCH - time of day must be late_night, contains only meals that are not large
CASUAL DRINK - any time of day, ratio of food to drinks less than 1.5. up to 3 drinks can have <=1.2 L of beer volume.
NOT_1 - either too many items ordered in a single step, or "kid" in one of the titles.

### Category 2:
In addition to the common occasions

ROMANTIC_DATE
FANCY_DATE
MALES_ONLY
JUST_EATING
BIRTHDAY
KIDS
NOT_2


### Category 3-5:
FAMILY EVENT - orders must contain kids dishes (order item title should be a kid dish)
SOCIAL GATHERING - any time of day, table must contain shareable dishes and not too many large not sharable dishes
AFTER WORK - a social gathering occurring after work hours (during the weekdays, around 15-18 pm)


### Category 6:
party events occurs if the guest count is larger than 10
FAMILY EVENT
SOCIAL GATHERING
AFTER WORK


## Guest Count Model - soon to come
