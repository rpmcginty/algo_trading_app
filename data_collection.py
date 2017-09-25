#%%
import numpy as np 
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
from utils import io
from alpha_vantage.timeseries import TimeSeries



#%% Set up api objects
apikey = io.load_key('alpha_vantage')
ts = TimeSeries(key=apikey,output_format='pandas')


#%%
data, meta_data = ts.get_intraday(symbol='MSFT',interval='60min', outputsize='full')


#%%
print data



