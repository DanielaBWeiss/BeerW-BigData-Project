# Heuristics

As defined earlier, our main goal is to define the consumer mission (ticket mission) - why did the consumer come here?  
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

### 1 guest tables
1. `Lunch`
2. `Dinner`
3. `Casual Drink and Meal`
4. `Drinking`
5. `Not Category 1`

Each occasion may also have a time sub-label one or more of the following:
- `lunch`
- `afternoon`
- `dinner`
- `late night`

### 2 guests tables


### 3-5 guests tables
1. `Family Event`
2. `Drinking`
3. `Breakfast`
4. `Lunch`
5. `Dinner`
6. `Social Gathering`
7. `After Work`

### 6+ guests tables
