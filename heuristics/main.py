import pandas as pd

from .bin_1 import Bin1Classifier
from .bin_2 import Bin2Classifier
from .bin_3to5 import Bin3to5Classifier
from .bin_6plus import Bin6PlusClassifier


data_path = "" # fix data path
data = pd.read_csv(data_path)

# 1. add features to data
# 2. shrink data to 1 entry (line) per table
# 3. for each entry, apply the relevant classifier based on the guest_count feature
