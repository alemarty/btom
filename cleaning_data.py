##python script 
#first run environment: .venv\Scripts\Activate.ps1

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

from sklearn.linear_model import LinearRegression
print("uploading packages")
from pathlib import Path

#----------------------------------------------------------------------------#
# Uploading the data 
#----------------------------------------------------------------------------#


WORKPATH = Path(r"C:\Users\Alejandra\Dropbox\Trade_regulation_Project2025")
DATAPATH = Path(r"C:\Users\Alejandra\Dropbox\Trade_regulation_Project2025\data_clean\working")
tradeEU_UK = DATAPATH / "working_data_EU_origin.dta"
tradeROW_UK = DATAPATH / "working_data_noEU_origin.dta"

# 3. Read the Stata file directly without manual conversion
df_EU= pd.read_stata(tradeEU_UK)
df_ROW_UK= pd.read_stata(tradeROW_UK)

#merge EU+row
df_EU = pd.concat([df_EU, df_ROW_UK], ignore_index=True)
del df_ROW_UK
gc.collect()

# clean sample 
df_EU['sample']  = all_trade['year'] >2022
df_EU = all_trade[all_trade['sample'] == True]

#clean prices (if eliminating completely run:)

df_EU['p1'] = df_EU.groupby(['COMCODE', 'year', 'ORIGIN'])['unit_price'].transform('quantile', 0.01)
df_EU['p99'] = df_EU.groupby(['COMCODE', 'year', 'ORIGIN'])['unit_price'].transform('quantile', 0.99)
df_EU= df_EU[(df_EU['unit_price']>df_EU['p1']) &  (df_EU['unit_price']<df_EU['p99'])].copy()

#if keep the original price.
#===is_outlier = (df_EU['unit_price'] < df_EU['p1']) | (df_EU['unit_price'] > df_EU['p99'])
#===df_EU['unit_price'] = np.where(is_outlier, np.nan, df_EU['unit_price'])
#-------------------------------------------------------------------------------#
 
##Append data 1 and 2 

