# BeerW-BigData-Project

Data Science project in collaboration with an Analytics company.

The goal of this project is to understand how to work with **Big Data**, do **data cleaning** and **processing**, and last but not least - **feature engineering** and **classification modeling**.

## Using our Code

### Data

1. Acquire the necessary data
2. Place them in the `Data` folder.

### Data Pre-Processing

The data needs to go through multiple steps in order to clean it, filter it for quality, and add features to it.

In the preprocess folder there exist multiple scripts for you to run.

1. **Textual Cleaning**
Run `python textual_cleaning.py` and make sure to change the name of the csv file to the one you have in the data folder.
This script saces the file: `df_1_text_processed.csv` under the `data` folder.

**TODO** - add argument handling in the script so we can pass in terminal

Textual cleaning takes care of removing *titles* with strings that indicate they are not really "meals".
Such as: 'sub', 'no -', 'extra', 'side', 'sauce'.
A few dictionary are also used in order to keep certain meals that *do* contain the above mentioned words in the title names.

2. **Adding Features **
Run `python adding_features.py` - saves `df_2_text_processed.csv` under the `data` folder.
This script reads the previously cleaned data, and adds multiple features using dictionaries and rules.

#### What features are we adding?
1. `category_id` - We sum all the category ids in each item of the total order, and add 6 separate columns for each one.
2. `total_order` - summing all items in an order
3. `order_day_of_week` - "Friday", "Monday", etc
4. `is_weekend` - is the order day landed on a weekend (friday - sunday)
5. `sharable` - is the item "title" a food that is a typical "sharing" food? (pizza, fries, wings, etc)
6. `kids_meal` - is the item a "kid" item
7. `birthday` - is there a comment in the order about a "birthday"
8. `order_hour` - the order_time hour
9. `period_of_day` - what part of the day did the order occur in (breakfast, lunch, etc)
10. `minute & hour time` - minute and hour of the order for - order_item_time and order_time_closed
11. `dwell_time` - the total time (in hours) the table order was open for
12. `meal_step` - the step in which the current item was ordered in. If the item was ordered after more than 4 minutes than the previous item, then the item is considered to be in the next numeric step. (1 - n steps, in increments of 1)
13. `meal_flow_step` - the "flow" step in which the current item was ordered in. The same as `meal_step`, except the increments are (time between the previous order / 4 minutes) - this means we consider "flow_steps" to be four minutes long. Each flow step is added the total flow steps up to that point.
14. `total_flow_steps` - the total flow steps in that order
15. `meal_flow_last_to_close` - the number of flow steps occurred, between the last item ordered, and till the table order was closed.
--

3. **Quality Filtering**
Run `python quality_filtering` - saves `df_3_text_processed.csv` under the `data` folder.
This script reads the previous data, and removes bars that are "untrustworthy", meaning they have data statistics that don't make sense.
Currently, we are only removing specific bars where their maximum guest counts only reach 0 or 1.


