import os

from slc_hunger_risk.config import data_dir
from slc_hunger_risk.comtrade import accumulate_data


os.makedirs(data_dir("processed"), exist_ok=True)

country = "Suriname"


hs_codes = [1006] #rice
years = [y for y in range(2010, 2022)]

for freq in ["A", "M"]:

    # Suriname does not report monthly trade flows
    if freq == "A":
        df = accumulate_data(hs_codes, years, reporters=[country], partners="all", freq=freq)
        df.to_csv(data_dir("processed", f"comtrade-data-reporter-{country}-{freq}.csv"), index=False)

    df = accumulate_data(hs_codes, years, reporters="all", partners=[country], freq=freq)
    df.to_csv(data_dir("processed", f"comtrade-data-partner-{country}-{freq}.csv"), index=False)




  