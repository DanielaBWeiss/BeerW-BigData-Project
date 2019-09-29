# Data Pre-Processing

The data needs to go through multiple steps in order to clean it, filter it for quality, and add features to it.  
We start with data of *15* features.

In the *pre-processing/* folder there exist multiple scripts for you to run.

**1. Textual Cleaning** <br />
Run `python textual_cleaning.py` and make sure to change the name of the csv file to the one you have in the data folder. <br />
This script saves the file: `df_1_text_processed.csv` under the `data` folder.  
In this step you should have *15* features (i.e. no new features were added).

&nbsp;&nbsp;**TODO** - add argument handling in the script so we can pass in terminal <br />

&nbsp;&nbsp;Textual cleaning takes care of removing *titles* with strings that indicate they are not really "meals".
&nbsp;&nbsp;Such as: 'sub', 'no -', 'extra', 'side', 'sauce'.
&nbsp;&nbsp;A few dictionaries are also used in order to keep certain meals that *do* contain the above mentioned words in the title   names.

&nbsp;&nbsp;**Note** - this script adds no new features <br />

**2. Adding Features** <br />
Run `python adding_features.py` - saves `df_2_text_processed.csv` under the `data` folder. <br />
This script reads the previously cleaned data, and adds multiple features using dictionaries and rules.  
In this step you should have *46* features.

&nbsp;**What features are we adding? (total of 31 new features)** <br />
  - `total_orders_category_id_X` - We sum all the category ids in each item of the total order, and add 6 separate columns for each one (X = 1.0 ... 6.0) \[6]
  - `total_orders` - total number of items in an order \[1]
  - `order_day_of_week` - "Friday", "Monday", etc \[1]
  - `is_weekend` - is the order day landed on a weekend (friday - sunday) \[1]
  - `sharable` - is the item "title" a food that is a typical "sharing" food? (pizza, fries, wings, etc) \[1]
  - `kids_meal` - is the item a "kid" item \[1]
  - `birthday` - is there a comment in the order about a "birthday" \[1]
  - `order(_close)_hour/minute` - the order(_close)_time hour & minute for start & close times \[4]
  - `order_item_hour/minute` - the order_item_time hour & minute \[2]
  - `period_of_day` - what part of the day did the order occur in (breakfast, lunch, etc) \[1]
  - `dwell_time` - the total time (in hours) the table order was open for \[1]
  - `meal_step` - the step in which the current item was ordered in. If the item was ordered after more than 4 minutes than the previous item, then the item is considered to be in the next numeric step. (1 - n steps, in increments of 1) \[1]
  - `meal_flow_step` - the "flow" step in which the current item was ordered in. The same as `meal_step`, except the increments are (time between the previous order / 4 minutes) - this means we consider "flow_steps" to be four minutes long. Each flow step is added the total flow steps up to that point \[1]
  - `total_flow_steps` - the total flow steps in that order \[1]
  - `meal_flow_last_to_close` - the number of flow steps occurred, between the last item ordered, and till the table order was closed \[1]
  - `total_meal_steps` - the total number of meal steps in that order \[1]
  - `first_to_second_order` - the time passed between the 2 first orders \[1]
  - `avg_time_between_steps` - average time between item orders in that order \[1]
  - `sit_to_order` - the time passed until the first item order \[1]
  - `max_items_per_step` - the highest count of items ordered in a step \[1]
  - `total_large_meals` - number of large meals in that order \[1]
  - `total_small_meals` - number of small meals in that order \[1]
<br />

**3. Quality Filtering** <br />
Run `python quality_filtering` - saves `df_3_text_processed.csv` under the `data` folder. <br />
This script reads the previous data, and removes bars that are "untrustworthy", meaning they have data statistics that don't  make sense.
Currently, we are only removing specific bars where their maximum guest counts only reach 0 or 1.
In this step you should have *48* features.

&nbsp;**What features are we adding? (total of 2 new features)** <br />
  - `total_sales_(before/inc)_tax` - total check for table \[2]