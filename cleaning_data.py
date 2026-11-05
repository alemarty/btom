
#Python code: created by AMC. 
#Purpose: clean data from Stata, generate trade statistics and graphs, run innitial regressions, export. 
#Date created: Nov 3 2026
#Last modified: Nov 4 2026
#----------------------------------------------------------------------------#
# Environment and cleanning
#----------------------------------------------------------------------------#
##python script 
#first run environment: .venv\Scripts\Activate.ps1
# Clear all user-defined variables in the current global scope
for var in list(globals().keys()):
    if not var.startswith("__") and var not in ['sys', 'gc']:
        del globals()[var]

import numpy as np
import pandas as pd
from pandas.io.stata import StataReader
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from pathlib import Path
from sklearn.linear_model import LinearRegression
print("uploading packages")

import sys
import gc

#----------------------------------------------------------------------------#
# Uploading the data and path setting
#----------------------------------------------------------------------------#

WORKPATH = Path(r"C:\Users\Alejandra\Dropbox\Trade_regulation_Project2025")
DATAPATH = Path(r"C:\Users\Alejandra\Dropbox\Trade_regulation_Project2025\data_clean\working")

tradeEU_UK = DATAPATH / "working_data_EU_origin.dta"
tradeROW_UK = DATAPATH / "working_data_noEU_origin.dta"

# 3. Read the Stata file directly without manual conversion
df_EU= pd.read_stata(tradeEU_UK) 
df_ROW_UK= pd.read_stata(tradeROW_UK) 
variable_labels_eu = StataReader(tradeEU_UK).variable_labels()
variable_labels_row = StataReader(tradeROW_UK).variable_labels()

#merge EU+row
df_EU = pd.concat([df_EU, df_ROW_UK], ignore_index=True)
del df_ROW_UK
gc.collect()

# clean sample 
df_EU['sample']  = df_EU['year'] >2022
df_EU = df_EU[df_EU['sample'] == True]

#clean prices (if eliminating completely run:)

df_EU['p1'] = df_EU.groupby(['COMCODE', 'year', 'ORIGIN'])['unit_price'].transform('quantile', 0.01)
df_EU['p99'] = df_EU.groupby(['COMCODE', 'year', 'ORIGIN'])['unit_price'].transform('quantile', 0.99)
df_EU= df_EU[(df_EU['unit_price']>df_EU['p1']) &  (df_EU['unit_price']<df_EU['p99'])].copy()

#if keep the original price (NaNs)
#===is_outlier = (df_EU['unit_price'] < df_EU['p1']) | (df_EU['unit_price'] > df_EU['p99'])
#===df_EU['unit_price'] = np.where(is_outlier, np.nan, df_EU['unit_price'])
#-------------------------------------------------------------------------------#
 
#create summary statistics 

df_EU = df_EU[['COMCODE', 'mode_ind_risk', 'mode_ind_risk_nona', 'monthac', 'month', 'unit_price', 'year', 'DISPATCH', 'ORIGIN', 'VALUE_GBP', 'QUANTITY_KG', 'EU_OR', 'EU_disp', 'FRAMEWORK', 'risk_eu', 'ind_norisk', 'ANIMAL_2digit', 'ANIMAL_4digit']]

print(variable_labels_eu)


# 1. Get raw counts including missing values
counts = df_EU['mode_ind_risk_nona'].value_counts(dropna=False)
# 2. Get percentages including missing values
percentages = df_EU['mode_ind_risk_nona'].value_counts(dropna=False, normalize=True) * 100
# 3. Combine into a clean table
stata_tab = pd.DataFrame({'Freq.': counts, 'Percent': percentages})
print(stata_tab)

summary_df = df_EU.groupby('year', 'COMCODE', 'ORIGIN', 'month', 'ANIMAL_4digit' ).agg({
    'unit_price': 'mean',          # Average of x
    'VALUE_GBP': 'mean',          # Average of y
    'QUANTITY_KG': 'mean',          # Average of z
    'mode_ind_risk': 'max',  # Maximum of another variable
    'other_var2': lambda x: x.mode()[0] if not x.mode().empty else None  # Mode of another variable
}).reset_index()