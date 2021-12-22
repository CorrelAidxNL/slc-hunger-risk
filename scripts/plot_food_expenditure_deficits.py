import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
from icecream import ic

from slc_hunger_risk.config import data_dir, plot_dir

os.makedirs(plot_dir(), exist_ok=True)

# CPI

scenarios = {
    "0": "income_rise_1.00",
    "0.25": "income_rise_1.36",
    "0.5": "income_rise_1.73",
    "0.75": "income_rise_2.09",
    "1": "income_rise_2.45",
}

diets = {
    "Energy Sufficient": "energy_sufficient", 
    "Nutrient Adequate": "nutrient_adequate",
    "Healthy": "healthy",
}

months = {
    "baseline": "2020_01",
    "scenario": "2021_10",
}

data = pd.read_csv(data_dir("clean", "food_expenditure_deficits.csv"))

ic(data)

dfs = []

for diet_label, diet_string in diets.items():

    columns = ["quantile", "population"] + [col for col in data.columns if diet_string in col]

    df = data[columns]
    df = pd.wide_to_long(
        df, 
        stubnames=[
            f"deficit_{diet_string}_{month}" for month in months.values()
        ] + [
            f"target_population_{diet_string}_{month}" for month in months.values()
        ], 
        i="quantile",
        j="scenario",
        sep="_",
        suffix=r'\S+'
    ).reset_index()

    df = pd.wide_to_long(
        df, 
        stubnames=[f"deficit_{diet_string}", f"target_population_{diet_string}"],
        i=["quantile", "scenario"],
        j="month",
        sep="_",
        suffix=r'\S+'
    ).reset_index()

    df = df.rename(columns={f"deficit_{diet_string}": "deficit", f"target_population_{diet_string}": "target_population"})

    for quantile in range(1, 6):
        for var in ["deficit", "target_population"]:
            df.loc[df[var].isna() & (df["quantile"] == quantile), var] = df.loc[
                (df["quantile"] == quantile) & (df["month"] == "2020_01") & (df["scenario"] == "income_rise_1.00"),
                var
            ].iloc[0]

    df["month"] = df["month"].str.replace("_", "-")

    df["diet"] = diet_label
    dfs.append(df)
    ic(df)

    extra_deficit = df.groupby(["scenario", "month"]).agg({"deficit": "sum"}).reset_index()
    extra_deficit = extra_deficit.pivot(index="scenario", columns="month", values="deficit")
    extra_deficit = (extra_deficit["2021-10"] - extra_deficit["2020-01"])
    ic(extra_deficit)

    df = df[df["scenario"].isin([scenarios[key] for key in ["0", "0.5", "1"]])].copy()
    rename_scenario = lambda incr, x, extra_deficit: (
        f"{int(float(x) * 100)}% CPI increase transmitted to incomes\n" 
        + (f"({incr} nominal incomes increase)\n" if incr != "1.00" else "(no nominal income increase)\n")
        + f"total extra deficit = {extra_deficit:.2f} mln USD"
    )
    scenarios_labels = {
        scenario_string: rename_scenario(scenario_string[-4:], scenario_label, extra_deficit.loc[scenario_string]) 
        for scenario_label, scenario_string in scenarios.items()
    }
    df["scenario"] = df["scenario"].replace(scenarios_labels)

    sns.set_theme(style="darkgrid")
    g = sns.catplot(
        data=df,
        kind="bar", 
        x="quantile", 
        y="deficit",
        col="scenario", 
        hue="month", 
    )
    g.despine(left=True, bottom=True)
    g.set(
        xlabel="Household consumption per capita, Quantile",
        ylabel="mln USD",
    )
    g.fig.suptitle(f"Monthly food expenditure deficit (estimate) | {diet_label} Diet", y=1.02)
    g.tight_layout()
    g.savefig(plot_dir(f"deficit_{diet_string}.png"), dpi=100)



exit()



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

