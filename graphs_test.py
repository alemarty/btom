
import stata_setup
stata_setup.config(r"C:\Program Files\StataNow19", "se") 
import pystata.stata as stata
from pystata import stata

stata.run(r'cd "C:\Users\Alejandra\Dropbox\Trade_regulation_Project2025\data_clean\working"')
stata.run("use working_data_intra_EU.dta, replace")
stata.run("des")
stata.run("collapse (mean) VALUE_GBP, by(year ORIGIN COMCODE )")
stata.run(r'cd "C:\Users\Alejandra\Documents\BTOM"')
stata.run("export delimited using  trade_agg.csv, replace")
stata.run("use  regressions_EU_2.dta, replace")
stata.run("export delimited using regressions.csv, replace")

##back to python 
import pandas as pd 
import numpy as np
import os
import matplotlib.pyplot as plt


#import statsmodels.api as sm
#import statsmodels.formula.api as smf
#from linearmodels.panel import PanelOLS
from linearmodels.iv.absorbing import AbsorbingLS

##where we want exit
path_fig = r"C:\Users\Alejandra\Documents\GitHub\Btom"

df= pd.read_csv("regressions.csv")
#convert to quarters 
df['qdate_set'] = pd.PeriodIndex(df['qdate'], freq='Q')
df['qdate_str'] = df['qdate_set'].astype(str)
df['id_panel'] = df.groupby(['ORIGIN', 'COMCODE']).ngroup()
##sorting panel
df=df.set_index(['id_panel', 'qdate_set'])
df = df.sort_values(by=['id_panel', 'qdate_set'])

#selecting sample
df=df[df['sample_reg']==1]

##regressions - relative to 2023q4: 

#####controls
df['control_fe'] = df.groupby(['qdate_set']).ngroup()
df['io_ip_interacted'] = df.groupby(['io', 'ip']).ngroup()
df['io_ip_cat'] = df['io_ip_interacted'].astype('category')
df['qdate_cat'] = df['qdate_str'].astype('category')
##### treatment
df["D_high"] = np.where(df["high_vs_rest"] == 1, df["qdate_str"], "2023Q4")

FE_to_absorb = df[['io_ip_cat', 'qdate_cat', 'io', 'ip']]

Y = df['luv_m']

#creates matrix 1-0 per period
interaction_dummies = pd.get_dummies(df['D_high'], drop_first=False)
#drop baseline 
if "2023Q4" in interaction_dummies.columns:
    interaction_dummies = interaction_dummies.drop(columns=["2023Q4"])

#create matrix X for regression
X = interaction_dummies.multiply(df['high_vs_rest'], axis=0).astype(float)

reg1 = AbsorbingLS(dependent=Y, exog=X, absorb=FE_to_absorb)
results_absorb = reg1.fit()

print(results_absorb)


coef_df = pd.DataFrame({
    'coef': results_absorb.params,
    'se': results_absorb.std_errors,
    'lower_ci': results_absorb.conf_int().iloc[:, 0],
    'upper_ci': results_absorb.conf_int().iloc[:, 1]
})
coef_df = coef_df.reset_index().rename(columns={'index': 'quarter'})

baseline_row = pd.DataFrame({
    'quarter': ['2023Q4'], 
    'coef': [0.0], 
    'se': [0.0], 
    'lower_ci': [0.0], 
    'upper_ci': [0.0]
})
coef_df = pd.concat([coef_df, baseline_row], ignore_index=True)
coef_df = coef_df.sort_values(by='quarter').reset_index(drop=True)
##figure


plt.figure(figsize=(8, 6))
plotline, caps, barlinecols =plt.errorbar(
    x=coef_df['quarter'], 
    y=coef_df['coef'], 
    yerr=[coef_df['coef'] - coef_df['lower_ci'], coef_df['upper_ci'] - coef_df['coef']],
    fmt='none',           # 'o' means circular markers for coefficients
    ecolor='#E4ECF8',     # Color of the CI lines
    linewidth=14,
    capsize=0      # Width of the horizontal caps on the CI bars
)

plt.scatter(
    coef_df['quarter'], 
    coef_df['coef'], 
    color='#3A86FF',       # Vibrant electric blue for the point estimates
    s=70,                  # Size of the circle marker
    zorder=3             # Ensures the dot sits cleanly on top of the background bar
    
)
plt.setp(barlinecols[0], capstyle='round')
plt.margins(x=0.08)
plt.axhline(y=0, color='#1b151888', linestyle='solid', linewidth=0.8, alpha=0.5)
plt.axvline(x='2023Q4', color='#1b151888', linestyle=':', linewidth=1.5)
#plt.title('', fontsize=14, fontweight='bold')
#plt.xlabel('Time', fontsize=12)
plt.grid(axis='y', linestyle=':', color='#CCCCCC', alpha=0.6)
plt.ylabel('Effect on unit value', fontsize=11, labelpad=10)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle=':', alpha=0.6)

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#E0E0E0')
ax.spines['bottom'].set_color('#E0E0E0')
ax.set_facecolor('#FFFFFF') # Clean crisp white background

plt.tight_layout()
plt.show()
full_path = os.path.join(path_fig, "luv_eu_eu_high_rest.png")
plt.savefig(full_path, dpi=300, bbox_inches="tight")
