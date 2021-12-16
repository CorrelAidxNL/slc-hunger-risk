import pandas as pd
import os
import seaborn as sns
from matplotlib import pyplot as plt
from slc_hunger_risk.config import data_dir, plot_dir

from icecream import ic

pd.set_option("max_rows", 200)
pd.set_option("max_seq_items", 200)


commodities = {
    "rice": "1006",
    "wheat": "1001",
    "wheat flour": "1101", 
    "sugar": "17",
    "live poultry": "0105",
    "poultry meat": "0207",
    "soybean oil": "1507",
}

flows = {
    "import": 1,
    "export": 2,
    "re-export": 3,
    "re-import": 4,
}

df_a = pd.read_csv(data_dir('processed', 'comtrade-data-partner-Suriname-A.csv'), dtype={"cmdCode": str})
df_m = pd.read_csv(data_dir('processed', 'comtrade-data-partner-Suriname-M.csv'), dtype={"cmdCode": str})
df_a_rep = pd.read_csv(data_dir('processed', 'comtrade-data-reporter-Suriname-A.csv'), dtype={"cmdCode": str})


def remove_aggregate_areas(df):
    codes = [0, 97]
    df = df[~df["rtCode"].isin(codes) & ~df["ptCode"].isin(codes)]
    return df

def aggregate_eu(df, by=[], reporter=True):
    area_cols = ["ptTitle", "ptCode"] if reporter else ["rtTitle", "rtCode"]
    eu_codes = [97, 276, 56, 528, 233, 428, 251, 203, 208, 381, 620, 724, 752, 348]
    df.loc[df[area_cols[1]].isin(eu_codes), area_cols] = ["EU", "EU"]
    df = df.groupby(by=area_cols+by).agg({"NetWeight": "sum", "TradeValue": "sum"}).reset_index()
    return df

def analyze_commodity_agg(df, commodity, flow, year_start, year_end, area_is_reporter=True):
    cmd_code = commodities[commodity]
    rg_code = flows[flow]
    df = df.copy()
    df = remove_aggregate_areas(df)
    df = df[(df["rgCode"] == rg_code) & (df["cmdCode"] == cmd_code)].copy()
    df = df[(year_start <= df["yr"]) & (df["yr"] <= year_end)]
    partner_cols = ["ptTitle", "ptCode"] if area_is_reporter else ["rtTitle", "rtCode"]
    df = df.groupby(by=partner_cols).agg({"NetWeight": "sum", "TradeValue": "sum"})
    df /= 1e6
    totals = df.sum()
    df[["NetWeight Pct", "TradeValue Pct"]] = (df.divide(totals) * 100).round(2)
    df = df.reset_index().drop(columns=partner_cols[1])
    df = df.rename(columns={partner_cols[0]: "Partner"})
    df["Partner"] = df["Partner"].replace({"United States of America": "USA"})
    df = df.sort_values(by=["NetWeight", "TradeValue"], ascending=False)
    df = df.set_index("Partner")
    df.loc["TOTAL"] = df.sum(axis=0)
    df = df.reset_index()
    return df




# commodities = [""]


partners = {
    "wheat": ["Germany", "Guyana"],
    "soybean oil": ["Brazil", "Netherlands", "Argentina", "Belgium"],
    "poultry meat": ["USA", "Brazil"],
    "rice": ["Portugal", "Brazil", "France", "Netherlands"], # Jamaica does not report monthly
}

labels = {
    "NetWeight": "Net Weight (1000 tonnes)",
    "CumulativeNetWeight": "Net Weight (cum. by month, 1000 tonnes)",
    "TradeValue": "Trade Value (mln USD)",
    "CumulativeTradeValue": "Trade Value (cum. by month, mln usd)",
    "UnitValue": "Unit Value (USD/kg)",
    "CumulativeUnitValue": "Unit Value (avg. until month, USD/kg)"
}

unit_values_to_impute = {
    "wheat": {
        ("Guyana", 2019): 0.30,
    },
    "poultry meat": {
        ("USA", 2020): 0.83,
    },
    "soybean oil": {},
    "rice": {},
}

def plot_monthly_trade(df, variable, commodity, flow, year_start, year_end, partner, area_is_reporter=True):
    cmd_code = commodities[commodity]
    rg_code = flows[flow]
    df = remove_aggregate_areas(df)
    df = df[(df["rgCode"] == rg_code) & (df["cmdCode"] == cmd_code)].copy()
    df = df[(year_start <= df["yr"]) & (df["yr"] <= year_end)]
    df["Month"] = df["period"].astype(str).str[4:6].astype(int)
    partner_cols = ["ptTitle", "ptCode"] if area_is_reporter else ["rtTitle", "rtCode"]
    df = df.drop(columns=partner_cols[1])
    df = df.rename(columns={partner_cols[0]: "Partner"}) 
    df = df.rename(columns={"yr": "Year"})
    df["Partner"] = df["Partner"].replace({"United States of America": "USA"})

    df = df[["Partner", "Year", "Month", "NetWeight", "TradeValue"]]
    df[["NetWeight", "TradeValue"]] /= 1e6

    for (p, y), u in unit_values_to_impute[commodity].items():
        df.loc[
            ((df["NetWeight"] == 0) | (df["NetWeight"].isna())) & (df["Partner"] == p) & (df["Year"] == y),
            "NetWeight"
        ] = df["TradeValue"] / u
    
    # print(df[df["NetWeight"] == 0])

    df.loc[~df["Partner"].isin(partners[commodity]), "Partner"] = "others"
    df = df.groupby(by=["Partner", "Year", "Month"]).agg({"NetWeight": "sum", "TradeValue": "sum"}).reset_index()

    df_tot = df.groupby(by=["Year", "Month"]).agg({"NetWeight": "sum", "TradeValue": "sum"}).reset_index()
    df_tot["Partner"] = "total"

    df = pd.concat([df, df_tot])


    df[["CumulativeNetWeight", "CumulativeTradeValue"]] = (
        df.groupby(by=["Partner", "Year"]).agg({"NetWeight": "cumsum", "TradeValue": "cumsum"})
    )

    df["UnitValue"] = df["TradeValue"] / df["NetWeight"]
    df["CumulativeUnitValue"] = df["CumulativeTradeValue"] / df["CumulativeNetWeight"]

    flow = "import" if (flow == "import" and area_is_reporter) or (flow == "export" and not area_is_reporter) else "export"
    df.to_csv(data_dir("clean", f"monthly-{flow}-{commodity.replace(' ', '_')}-{year_start}-{year_end}.csv"), index=False)


    sns.set_theme(style="darkgrid")
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.lineplot(data=df[df["Partner"] == partner], x="Month", y=variable, hue="Year", style="Year", 
        markers=True, dashes=False, ax=ax)
    sns.despine(left=True, bottom=True)
    ax.set(
        title=f"{commodity} {flow}s, {'' if partner=='total' else 'partner='}{partner}",
        ylabel=labels[variable],
        xticks=[m for m in range(1,13)],
        ylim=(0 if "UnitValue" in variable else None, None),
    )
    ax.legend(title="Year", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    fig.tight_layout()
    fig.savefig(plot_dir("comtrade", f"{variable}_{flow}_{commodity.replace(' ', '_')}_{partner.replace(' ', '_')}.png"), dpi=100)

    plt.close()


if __name__ == "__main__":

    for commodity in ["wheat", "soybean oil", "poultry meat"]:
        print("Commodity: ", commodity, "\n")
        year_start, year_end = 2016, 2020
        for df, flow, is_reporter in zip([df_a_rep, df_a, df_m], ["import", "export", "export"], [True, False, False]):
            print(analyze_commodity_agg(df, commodity, flow, year_start, year_end, is_reporter), "\n")
    for commodity in ["rice"]:
        print("Commodity: ", commodity, "\n")
        year_start, year_end = 2016, 2020
        for df, flow, is_reporter in zip([df_a_rep, df_a, df_m], ["export", "import", "import"], [True, False, False]):
            print(analyze_commodity_agg(df, commodity, flow, year_start, year_end, is_reporter), "\n")

    os.makedirs(plot_dir("comtrade"), exist_ok=True)

    for commodity in ["wheat", "soybean oil", "poultry meat"]:
        year_start, year_end = 2016, 2021
        for variable in labels.keys():
            if not "Cumulative" in variable:
                continue
            plot_monthly_trade(df_m, variable, commodity, "export", year_start, year_end, "total", area_is_reporter=False)
            for partner in partners[commodity]:
                plot_monthly_trade(df_m, variable, commodity, "export", year_start, year_end, partner, area_is_reporter=False)

    for commodity in ["rice"]:
        year_start, year_end = 2016, 2021
        for variable in labels.keys():
            if not "Cumulative" in variable:
                continue
            plot_monthly_trade(df_m, variable, commodity, "import", year_start, year_end, "total", area_is_reporter=False)
            for partner in partners[commodity]:
                plot_monthly_trade(df_m, variable, commodity, "import", year_start, year_end, partner, area_is_reporter=False)



    




