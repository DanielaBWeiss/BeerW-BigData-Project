# Heuristics

As defined earlier, our main goal is to define the consumer mission (ticket mission) - why did the consumer come here?  
It is a hard problem.

Here, we'll specify the different occasions (there are various of occasions, some specific to certain guest counts).  
There will be 4 different heuristics, one for each bin:
- 1 guest tables
- 2 guests tables
- 3-5 guests tables
- 6+ guests tables

Then, a main script (called `main.py`) will take care of applying the relevant heuristic based on the *guest_count* for each table.

## Occasions

### 1 guest tables


### 2 guests tables
1. `Lunch`
2. `Dinner`
3. `Casual Drink and Meal`
4. `Drinking`

Each occasion may also have a time sub-label one or more of the following:
- `lunch`
- `afternoon`
- `dinner`
- `late night`

### 3-5 guests tables
1. `Family Event`
2. `Drinking`
3. `Breakfast`
4. `Brunch`
5. `Lunch`
6. `Dinner`
7. `Social Gathering`
8. `After Work`

### 6+ guests tables
