import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
from icecream import ic

from slc_hunger_risk.config import data_dir, plot_dir

os.makedirs(plot_dir(), exist_ok=True)

# CPI

baseline_year, baseline_month = 2020, 1

df = pd.read_csv(data_dir("processed", "ABS_Sur_CPI.csv"))

# Normalize to baseline
for col in df.columns[2:]:
    df[col] /= df.loc[(df["Year"] == baseline_year) & (df["Month"] == baseline_month), col].iloc[0] / 100

df["Date"] = pd.to_datetime({"year": df["Year"], "month": df["Month"], "day": 1})
df = df.rename(columns={"Food and Non Alcoholic Beverages": "Food"})
df["Food / Total"] = df["Food"] / df["Total"] * 100
df = df.melt(id_vars="Date", value_vars=["Food", "Total", "Food / Total"], var_name="Category", value_name="Consumer Price Index")

ic(df)

sns.set_theme(style="darkgrid")
fig, ax = plt.subplots(figsize=(6, 4))
sns.lineplot(
    data=df, 
    x="Date", 
    y="Consumer Price Index", 
    hue="Category", 
    style="Category",
    markers=True, 
    dashes=False,
    ax=ax,
)
sns.despine(left=True, bottom=True)
ax.set(
    title="Consumer Price Index (Jan 2020 = 100)",
    ylabel=None,
    xlabel=None,
)
ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
fig.tight_layout()
fig.savefig(plot_dir("cpi.png"), dpi=100)

plt.close()

# Exchange rate

df = pd.read_csv(data_dir("processed", "CBVS_exchange_rates.csv"))

df["Date"] = pd.to_datetime(df["Time_Period"])
df[" "] = " "

fig, ax = plt.subplots(figsize=(5, 4))
sns.lineplot(
    data=df[df["Date"] >= pd.to_datetime("2016-04-01")], 
    x="Date", 
    y="EXR_SDR_USD",
    style=" ", 
    markers=True, 
    dashes=False,
    legend=False,
    ax=ax,
)
sns.despine(left=True, bottom=True)
ax.set(
    title="Exchange Rate USD to SRD",
    ylabel=None,
    xlabel=None,
)
fig.tight_layout()
fig.savefig(plot_dir("usd_srd.png"), dpi=100)

