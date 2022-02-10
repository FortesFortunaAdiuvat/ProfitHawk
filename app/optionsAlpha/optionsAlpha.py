import pandas as pd
import numpy as np
#import pandas.io.data as web
from pandas_datareader import data
from datetime import datetime

import matplotlib.pyplot as plt
#%matplotlib inline

pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 7)
pd.set_option('display.max_rows', 15)
pd.set_option('display.width', 82)
pd.set_option('precision', 3)

aapl_options = data.Options('AAPL', 'yahoo')
print(aapl_options)
