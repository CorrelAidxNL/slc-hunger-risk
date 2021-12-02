import seaborn as sns
import matplotlib.pyplot as plt
import os

from slc_hunger_risk.config import plot_dir
from slc_hunger_risk.generate_baseline_data import generate_baseline_data

os.makedirs(plot_dir(), exist_ok=True)

baseline_years = [2016,2017,2018]
country = "Suriname"

# Get baseline data
df = generate_baseline_data(country, baseline_years)
# Plot food supply in kcal by item
df = df[df["Element"] == "Food supply (kcal/capita/day)"]
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


