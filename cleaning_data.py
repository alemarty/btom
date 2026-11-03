##python script 
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
DATAPATH = Path(r"C:\Users\Alejandra\Dropbox\Trade_regulation_Project2025\data_clean")
tradeEU_UK = DATAPATH / "working_data_EU_origin.dta"
tradeROW_UK = DATAPATH / "working_data_noEU_origin.dta"

# 3. Read the Stata file directly without manual conversion
df_EU= pd.read_stata(tradeEU_UK)

