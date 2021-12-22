import pandas as pd
from samplics.estimation import TaylorEstimator


def estimate(df, variable, domain_var=None, parameter="mean", weight="weight2020"):
    estimator = TaylorEstimator(parameter)
    estimator.estimate(
        y = df[variable],
        samp_weight= df[weight],
        stratum = df["stratum"],
        psu = df["psu"],
        domain = df[domain_var] if domain_var else None,
        remove_nan = True,
    )
    res = estimator.to_dataframe()
    res.columns = [col[1:] for col in res.columns]
    res = res.drop(columns="parameter")
    res = res.rename(columns={"estimate": variable, "domain": domain_var})
    if domain_var is None:
        res = res.iloc[0].to_dict()
        print(res)
    return res


def find_quantiles(df, variable, weight="weight2020", q=5):
    df = df[[weight, variable]].dropna().copy()
    df = df.groupby(by=variable).sum().reset_index()
    df = df.sort_values(by=variable, ascending=True)
    df["cum_prob"] = df[weight].cumsum() / df[weight].sum()
    quantiles = [df[variable].iloc[0] - 1e-6]
    probabilities = [0]
    for n in range(1, q):
        idx = abs(df["cum_prob"] - n / q).idxmin()
        quantiles.append(df.loc[idx, variable])
        probabilities.append(df.loc[idx, "cum_prob"])
    quantiles += [df[variable].iloc[-1]]
    probabilities += [1]
    probabilities = [probabilities[i+1] - probabilities[i] for i in range(q)]
    return quantiles, probabilities


def assign_quantiles(df, quantiles, variable):
    q = len(quantiles) - 1
    df["quantile"] = 1
    df[f"{variable}_min"] = quantiles[0]
    df[f"{variable}_max"] = quantiles[1]
    for i in range(1, q):
        var_min, var_max = quantiles[i:i+2]
        df.loc[
            (var_min < df[variable]) & (df[variable] <= var_max), 
            ["quantile", f"{variable}_min", f"{variable}_max"]
        ] = [i + 1, var_min, var_max]
    return df