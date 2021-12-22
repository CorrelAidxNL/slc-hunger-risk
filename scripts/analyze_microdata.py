import pandas as pd
import numpy as np
import os
import seaborn as sns
from matplotlib import pyplot as plt

from slc_hunger_risk.microdata import find_quantiles, assign_quantiles, estimate
from slc_hunger_risk.config import data_dir, plot_dir

from icecream import ic

pd.set_option("max_rows", 200)
pd.set_option("max_seq_items", 200)

# Load consumer price index to deflate nominal values

df_cpi = pd.read_csv(data_dir("processed", "ABS_Sur_CPI.csv"))

get_overall_cpi = lambda year, month: df_cpi.loc[(df_cpi["Year"] == year) & (df_cpi["Month"] == month), "Total"].iloc[0]
get_food_cpi = lambda year, month: df_cpi.loc[(df_cpi["Year"] == year) & (df_cpi["Month"] == month), "Food and Non Alcoholic Beverages"].iloc[0]
get_avg_food_cpi = lambda year: df_cpi.loc[(df_cpi["Year"] == year), "Food and Non Alcoholic Beverages"].mean()


baseline_year, baseline_month = 2020, 1

# Food cost estimates

df_exch = pd.read_csv(data_dir("processed", "CBVS_exchange_rates.csv"))

get_usd_to_srd = lambda year, month: df_exch.loc[df_exch["Time_Period"] == f"{year}-{month:02d}", "EXR_SDR_USD"].iloc[0]
get_avg_usd_to_srd = lambda year: df_exch.loc[df_exch["Time_Period"].str.startswith(f"{year}"), "EXR_SDR_USD"].mean()

# Source: data/raw/idb/Suriname_SLC/07_Web/MicroData_Poverty/01_Readme_poverty_data.pdf
df_food_cost = pd.DataFrame({
    "domain": ['Great Paramaribo', 'Rest of the coastal region', 'Interior', 'Total'],
    "SLC_energy_sufficient": [265.29, 250.48, 206.69, 258.65]
})

df_food_cost["SLC_energy_sufficient"] *= get_food_cpi(baseline_year, baseline_month) / get_food_cpi(2017, 6)

days_in_month = 30.4375
conversion_to_baseline = get_avg_usd_to_srd(2017) * days_in_month * get_food_cpi(baseline_year, baseline_month) / get_avg_food_cpi(2017)

# Source: https://www.unicef.org/media/72676/file/SOFI-2020-full-report.pdf
df_food_cost["FAO_energy_sufficient"] = [np.nan] * 3 + [1.14 * conversion_to_baseline]
df_food_cost["FAO_nutrient_adequate"] = [np.nan] * 3 + [3.25 * conversion_to_baseline]
df_food_cost["FAO_healthy"] = [np.nan] * 3 + [5.09 * conversion_to_baseline]

ic(df_food_cost)

# Necessary non-food expenses

df_nonfood = pd.DataFrame({
    "domain": ['Great Paramaribo', 'Rest of the coastal region', 'Interior', 'Total'],
    "SLC_nonfood": [733.10, 590.23, 533.27, 691.31]
})

df_nonfood["SLC_nonfood"] *= get_food_cpi(baseline_year, baseline_month) / get_food_cpi(2017, 6)

# Number of quantiles

q = 5

# Load SLC data

df = pd.read_stata(data_dir('raw', 'idb', 'Suriname_SLC', '07_Web', 'MicroData_Poverty', '1 Suriname', 'Analysis','SSLC_00_12a_13_16_singles_Housing.dta'))

df = df[["hhid", "domain", "weight3", "stratum", "psu", "cons_pc", "food_pc", "hh_size"]]
df["food_cons_share"] = df["food_pc"] / df["cons_pc"]
for var in ["cons_pc", "food_pc"]:
    df[var] *= get_overall_cpi(baseline_year, baseline_month) / get_overall_cpi(2017, 6)


# Find consumption per capita quantiles

variable = "cons_pc"
weight = "weight3"

quantiles, probabilities = find_quantiles(df, variable, weight=weight, q=q)
df = assign_quantiles(df, quantiles, variable)


# Consider different scenarios for food spending deficits

scenario_year, scenario_month = 2021, 10


def calculate_deficits(df, scenario_year=baseline_year, scenario_month=baseline_month, nominal_income_rise=1):
    diets = ["energy_sufficient", "nutrient_adequate", "healthy"]
    for diet in diets:
        food_cost = df_food_cost.copy().loc[df_food_cost["domain"] == "Total", f"FAO_{diet}"].iloc[0]
        nonfood = df_nonfood.copy().loc[df_nonfood["domain"] == "Total", "SLC_nonfood"].iloc[0]
        budget = df["cons_pc"].copy()
        # Implement scenarios for food cost, nonfood and budget
        food_cost *= get_food_cpi(scenario_year, scenario_month) / get_food_cpi(baseline_year, baseline_month)
        nonfood *= get_overall_cpi(scenario_year, scenario_month) / get_overall_cpi(baseline_year, baseline_month)
        budget *= nominal_income_rise
        suffix = f"{diet}_{scenario_year}_{scenario_month:02d}_income_rise_{nominal_income_rise:.2f}"
        df[f"deficit_{suffix}"] = np.minimum(food_cost, np.maximum(
            nonfood + food_cost - budget,
            0,
        )) * df["hh_size"]
        df[f"target_population_{suffix}"] = np.where(df[f"deficit_{suffix}"] > 0, df["hh_size"], 0)
        # For numerical reasons
        df[f"deficit_{suffix}"] += 1e-12
        df[f"target_population_{suffix}"] += 1e-12
    return df

# Baseline deficits
df = calculate_deficits(df)
# Convert into 2021-10 SRD
for col in df:
    if "deficit" in col:
        df[col] *= get_overall_cpi(scenario_year, scenario_month) / get_overall_cpi(baseline_year, baseline_month)

# Scenarios
nominal_income_rises = [
    x * get_overall_cpi(scenario_year, scenario_month) / get_overall_cpi(baseline_year, baseline_month) + 1 - x
    for x in [0, 0.25, 0.5, 0.75, 1.0]
]
for nominal_income_rise in nominal_income_rises:
    df = calculate_deficits(df, scenario_year, scenario_month, nominal_income_rise)


# Estimate variables per quantile
df["population"] = df["hh_size"]
estimates_2017 = {}
variables_per_quantile = (
    ["hh_size", "cons_pc", "food_pc", "food_cons_share"] 
    + [col for col in df.columns if "deficit" in col or "population" in col]
) 

for var in variables_per_quantile:
    estimates_2017[var] = estimate(
        df, 
        variable=var,
        domain_var="quantile", 
        weight=weight,
        parameter="mean" if not ("deficit" in var or "population" in var) else "total"
    )
df_2017 = pd.concat(
    [est.set_index("quantile").iloc[:, 0] for est in estimates_2017.values()],
    axis=1
).reset_index()
ic(df_2017)

# Convert deficits into mln USD

for col in df_2017.columns:
    if "deficit" in col:
        df_2017[col] /= get_usd_to_srd(2021, 10) * 1e6

# Rescale the numbers so they match the total population of 2020

population_2020 = 586634
scale = population_2020 / df_2017["population"].sum()

for col in df_2017.columns:
    if "population" in col or "deficit" in col:
        df_2017[col] *= scale

# Add quantile ranges

df_2017[f"{variable}_min"] = quantiles[:q]
df_2017[f"{variable}_max"] = quantiles[1:]




df_2017.to_csv(data_dir("clean", "food_expenditure_deficits.csv"), float_format='{:.3f}'.format, index=False)


# Load Covid 19 survey data

df = pd.read_csv(data_dir('raw', 'idb', 'Suriname-Survey-Data-May21', 'Data', 'suriname_covid19.csv'))

columns = ["incjan", "spnjan", "incjun", "spnjun"]

df = df[["hhid", "great_par", "district", "weight2020", "stratum", "psu", "memnum", "newnum"] + columns]

df[columns] = df[columns].replace({".a": np.nan, "-99": np.nan})
df[columns] = df[columns].astype(float)

for var in ["incjan", "spnjan"]:
    df[var] *= get_overall_cpi(baseline_year, baseline_month) / get_overall_cpi(2020, 1)

for var in ["incjun", "spnjun"]:
    df[var] *= get_overall_cpi(baseline_year, baseline_month) / get_overall_cpi(2020, 6)


# Calculate per capita values

df["hh_size"] = df[["memnum", "newnum"]].sum(axis=1).astype(int)
# df["hh_size"] = df["memnum"]

for col in columns:
    df[f"{col}_pc"] = df[col] / df["hh_size"]

df["spn_pc"] = df[["spnjan_pc", "spnjun_pc"]].mean(axis=1)

variable = "spn_pc"
weight = "weight2020"

quantiles, probabilities = find_quantiles(df, variable, weight=weight, q=q)
df = assign_quantiles(df, quantiles, variable)

# Assume food share of spending follows the quantile-dependence of the SLC data and estimate food spending per capita

food_cons_share = estimates_2017["food_cons_share"].iloc[:, :2]

df = df.merge(food_cons_share, on="quantile", how="left")
df["food_pc"] = df["food_cons_share"] * df[variable]


variables_per_quantile = ["hh_size", "spn_pc", "food_pc"]
estimates_2020 = {}
for var in variables_per_quantile:
    estimates_2020[var] = estimate(
        df, 
        variable=var,
        domain_var="quantile", 
        weight=weight,
    )
df_2020 = pd.concat(
    [est.set_index("quantile").iloc[:, 0] for est in estimates_2020.values()],
    axis=1
).reset_index()
ic(df_2020)
























exit()

# ic(estimate(df, "incjun"))


# Plot

os.makedirs(plot_dir("microdata"), exist_ok=True)

x_max = df[columns].max().max()
N = 5000
x_list = np.linspace(0, x_max + 1, N)

sns.set_theme(style="darkgrid")

for variable in columns:
    ic(variable)

    # y_list = []
    w_list = []
    for x in x_list:
        df_x = df[df[variable] <= x]
        # df_x.loc[:, "count"] = 1
        # if len(df_x) < 1:
        #     y_list.append(0)
        # else:
        #     res = estimate(df_x, "count", parameter="total")
        #     y_list.append(res["estimate"])
        w_list.append(df_x["weight2020"].sum())


    fig, ax = plt.subplots(figsize=(5, 4))
    # ax.plot(x_list, y_list, label="count est.")
    total = w_list[-1]
    w_list = [w / total for w in w_list]
    ax.plot(x_list, w_list)
    ax.set_xlabel(f"x (SRD)")
    ax.set_ylabel(f"Proportion of HH with {variable} ≤ x")
    ax.set_xscale("log")
    fig.tight_layout()
    fig.savefig(plot_dir("microdata", f"{variable}_cumulative_dist.png"), dpi=100)







