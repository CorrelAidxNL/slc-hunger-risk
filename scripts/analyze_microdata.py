import pandas as pd
import numpy as np
import os
import seaborn as sns
from matplotlib import pyplot as plt
from samplics.estimation import TaylorEstimator
from slc_hunger_risk.config import data_dir, plot_dir

from icecream import ic

pd.set_option("max_rows", 200)
pd.set_option("max_seq_items", 200)


df = pd.read_csv(data_dir('raw', 'idb', 'Suriname-Survey-Data-May21', 'Data', 'suriname_covid19.csv'))

ic(df.columns)

columns = ["incjan", "spnjan", "incjun", "spnjun"]

df[columns] = df[columns].replace({".a": np.nan, "-99": np.nan})
df[columns] = df[columns].astype(float)

# for col in columns:
#     ic(col, df[col].unique())


def estimate(df, variable, parameter="mean"):
    estimator = TaylorEstimator(parameter)
    estimator.estimate(
        y = df[variable],
        samp_weight= df["weight2020"],
        stratum = df["stratum"],
        psu = df["psu"],
        remove_nan = True,
    )
    res = estimator.to_dataframe()
    return {"value": res.loc[0, "_estimate"], "error": res.loc[0, "_stderror"]}


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
        #     y_list.append(res["value"])
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







