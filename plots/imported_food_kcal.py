# -*- coding: utf-8 -*-
"""
Script for downloading and analysing food supply of proteins Suriname
"""
import sys

sys.path.append( 'C:\\Users\\valer\\OneDrive\\Dokumente\\CVs _ Applications\\\Correlaid 2021\\slc-hunger-risk-main\\src')
sys.path.append( 'C:\\Users\\valer\\OneDrive\\Dokumente\\CVs _ Applications\\\Correlaid 2021/src')


import seaborn as sns
import matplotlib.pyplot as plt
import os
import pandas as pd

path = 'C:\\Users\\valer\\OneDrive\\Dokumente\\CVs _ Applications\\Correlaid 2021\\slc-hunger-risk-main\\src'

os.chdir(path)

from slc_hunger_risk.config import plot_dir
from slc_hunger_risk.generate_baseline_data import generate_baseline_data

os.makedirs(plot_dir(), exist_ok=True)

baseline_years = [2016,2017,2018]
country = "Suriname"

# Get baseline data
df_all = generate_baseline_data(country, baseline_years)
# Plot food supply in kcal by item
df = df_all[df_all["Element"] == "Food supply (kcal/capita/day)"]
# Sort by values & remove zero entries
df = df.sort_values(by="Value", ascending=False)
df = df[df["Value"] > 0]
# Keep the top n, aggregate the rest
n = 30
df = df.reset_index(drop=True)
df["id"] = df.index
df.loc[df.index >= n, ["id", "Item"]] = [n, "Others"]
df = df.groupby(by="id").agg({"Value": "sum", "Item": "first"}).reset_index()


# Plot
sns.set_theme(style="darkgrid")
# sns.set_color_codes("pastel")
# Initialize the matplotlib figure
fig, ax = plt.subplots(figsize=(8, 12))
sns.barplot(data=df, x="Value", y="Item", color="b")
sns.despine(left=True, bottom=True)
ax.set(
    ylabel="", 
    xlabel="Food supply (kcal/capita/day)", 
    title=f"{country}, {baseline_years[0]}-{baseline_years[-1]} average",
)

fig.tight_layout()
fig.savefig(plot_dir(f"food-supply-{country}-{baseline_years[0]}-{baseline_years[-1]}.png"), dpi=100)


#Get conversion factors using the "food" element, which is total supply by food item
#import food
df_food = df_all[df_all["Element"] == "Food"]
df_food = df_food.sort_values(by="Value", ascending=False)
df_food = df_food[df_food["Value"] > 0]

#import quantity of imports and domestic supply quantity
df_imports = df_all[df_all["Element"] == "Import Quantity"]
df_dom_supply = df_all[df_all["Element"] == "Domestic supply quantity"]

#merge df (which has the supply in kcal/capita) with df_food
df = pd.merge(df, df_food, on = "Item")
df = df.rename(columns={"Value_x": "Value_supply_kcal", "Value_y": "Value_supply_tonnes"})
#Create variable that is conversion rate
df["Conversion"] = df["Value_supply_tonnes"] / df["Value_supply_kcal"]

#merge df with df_imports
df = pd.merge(df, df_imports, on = "Item")
df = df.rename(columns = {"Value": "Value_Quant_import"})
df["Imports_kcal"] = df["Value_Quant_import"] / df["Conversion"]

#merge df with df_dom_supply
df = pd.merge(df, df_dom_supply, on = "Item")
df = df.rename(columns = {"Value": "Value_dom_supply"})
df = df.sort_values(by="Value_supply_kcal", ascending=False)
df = df[:15]

#Plot kcal provided by imported foods against domestic supply quantity (both in kcal)
sns.set_theme(style="darkgrid")
# Initialize the matplotlib figure
fig, ax = plt.subplots(figsize=(12,8))
sns.barplot(data=df, x="Value_supply_kcal", y="Item", color = "b")
sns.set_color_codes("dark")
sns.barplot(data=df, x="Imports_kcal", y="Item", color = "b")
sns.despine(left=True, bottom=True)
ax.set(
    ylabel="", 
    xlabel="Imports as proportion of domestic supply of food in kcal/capita/day", 
    title=f"{country}, {baseline_years[0]}-{baseline_years[-1]} average"
)

fig.tight_layout()
fig.savefig(plot_dir(f"food-supply-imports-{country}-{baseline_years[0]}-{baseline_years[-1]}.png"), dpi=100)
