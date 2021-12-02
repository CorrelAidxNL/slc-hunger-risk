import pandas as pd

from .config import data_dir, dtype_fao


def load_food_balance_data(country):
    df = pd.read_csv(data_dir("processed", f"fao-data-{country}.csv"), dtype=dtype_fao)
    # Select Food Balance Sheet elements
    elements = [
        "Food supply (kcal/capita/day)", 
        "Food",
        "Production", 
        "Import Quantity", 
        "Export Quantity",
        "Domestic supply quantity",
        "Stock Variation",
    ]
    df = df[df["Element"].isin(elements)]
    # Select Food Balance Sheet items; their codes are in range 2510-2700
    df = df[(2510 < df["Item Code"]) & (df["Item Code"] < 2900)]
    # Select only relevant columns
    df = df[["Year", "Item", "Item Code", "Element", "Value", "Unit", "Flag"]]
    # Values should be floats
    df["Value"] = df["Value"].astype(float)
    # Years should be ints
    df["Year"] = df["Year"].astype(int).astype("Int64")
    return df

def generate_baseline_data(country, baseline_years, force=False):
    file = data_dir("clean", f"fao-baseline-data-{baseline_years[0]}-{baseline_years[-1]}.csv")
    if not force and file.exists():
        return pd.read_csv(file)
    df = load_food_balance_data(country)
    # Limit data range to baseline_years
    df = df[df["Year"].isin(baseline_years)]
    # We will aggregate data; this does not make sense for Stock Variation
    df = df[df["Element"] != "Stock Variation"]
    # Aggregate by element and item, average over years
    df = df.drop(columns="Year").groupby(by=["Element", "Item"]).agg({
        "Item Code": "first", 
        "Value": "mean",
        "Unit": "first", 
        "Flag": lambda x: ",".join(x), 
    }).reset_index()
    df.to_csv(file, index=False)
    return df
    





