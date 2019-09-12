import pandas as pd

#Change name here to add to saved csv file
name="valentine"
data = pd.read_csv("../data/toronto_valentine_20190210_20190216.csv")

data = data.dropna()
# Dropping Unrelevant Titles, except those appearing in dictionaries
sauces = set()
sub = set()

def filter_titles(row):
    title = row["title"].lower()
    price = row["sales_before_tax"]

    if "xtra" in title:
        return False
    if "sub" in title and price == 0:
        sub.add(title)
        return False
    elif "add" in title:
        return False
    elif "sauce" in title:
        for t in foods_w_sauce: 
            if t in title: return True
        for t in remove_w_sauce:
            if t in title: return False
        sauces.add(title)
        return False
    elif "no " in title:
        return False
    elif "no." in title:
        return False
    elif "-no " in title:
        return False
    elif "side " in title:
        return False
    elif "+" in title:
        return False
    elif "dip" in title:
        return False
    elif "blue cheese" in title:
        return False
    elif "bbq" in title:
        return False
    elif "n/c" in title:
        return False
    elif "s/o" in title:
        return False
    elif title == '' or title == 'garlic.aioli' or title == 'gluten' or title == 'hot n honey' or title == 'honey garlic' or title == 'kids.' or title == 'to go':
        return False
    else:
        return True

foods_w_sauce = ["fingers", "spaghetti", "poutine", "wings", "pate", "bowl", "fries", "rigatoni", "pasta",
                "linguini", "frite"]
remove_w_sauce = ["no wing", "for wing", "on", "side"]
whitelist = set('.abcdefghijklmnopqrstuvwxyz \\//')
    
data.title = data.title.apply(lambda x: str(x))
data = data[data.apply(lambda x: filter_titles(x), axis=1)]

data.to_csv("../data/"+name+"_1_text_processed.csv", index=False)