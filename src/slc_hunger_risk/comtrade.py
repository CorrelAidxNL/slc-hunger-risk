import itertools
import json
import pandas as pd
import numpy as np
from pprint import pprint
import time
import requests


def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def list_to_string(l):
    if not isinstance(l, list):
        return str(l)
    else:
        return ",".join([str(x) for x in l])


def list_all_months(year):
    return [f"{year}{m:02d}" for m in range(1, 13)]


def get_area_codes():
    response = requests.get("https://comtrade.un.org/Data/cache/reporterAreas.json")
    response.encoding = "utf-8-sig"
    area_codes = {res["text"]: res["id"] for res in response.json()["results"]}
    return area_codes


def request_availability(reporter_codes, years, type="C", freq="M", px="HS", **kwargs):
    assert (px == "HS" if freq == "M" else True) # for monthly data only "as reported" HS codes
    url = "https://comtrade.un.org/api//refs/da/view"
    if freq == "M":
        assert (isinstance(years, int))
    parameters = {
        "r": list_to_string(reporter_codes),
        "ps": list_to_string(list_all_months(years) if freq == "M" else years),
        "type": type,
        "freq": freq,
        "px": px
    }
    response = requests.get(url, params=parameters)
    return response.json()


def get_data(reporter_codes, partner_codes, years, commodity_codes,
             type="C", freq="M", px="HS", rg="all", max="50000", head="M", fmt="json"):
    assert (px == "HS" if freq == "M" else True) # for monthly data only "as reported" HS codes
    url = "http://comtrade.un.org/api/get"
    if freq == "M":
        assert (isinstance(years, int))
    parameters = {
        "r": list_to_string(reporter_codes),  # max 5
        "p": list_to_string(partner_codes),  # 201001 # max 5
        "ps": list_to_string(list_all_months(years) if freq == "M" else years),  # max 5
        "cc": list_to_string(commodity_codes),  # max 20
        "type": type,
        "freq": freq,
        "px": px,
        "rg": rg,
        "max": max,  # max 50 000
        "head": head,
        "fmt": fmt
    }
    pprint(parameters)
    response = requests.get(url, params=parameters)
    print("Response status code:", response.status_code)
    assert (response.status_code == 200)
    return response.json()["dataset"], response.json()["validation"]


def accumulate_data(hs_codes, years, reporters, partners, freq="M", parts=1, px="HS", rg="all", check_avail=False):

    hs_codes = [x.tolist() for x in np.array_split(hs_codes, parts)]
    area_codes = get_area_codes()
    query = {
        "years": years[0],
        "commodity_codes": hs_codes[0], # max 20
        "reporter_codes": [area_codes[area] for area in reporters] if reporters != "all" else "all", # max 5
        "partner_codes": [area_codes[area] for area in partners] if partners != "all" else "all",
        "freq": freq,
        "px": px,
        "rg": rg
    }
    df_list = []
    # Seperate API request for each year
    for year, part in itertools.product(years, range(parts)):
        query["years"] = year
        query["commodity_codes"] = hs_codes[part]
        print(f"Query: {year}, part {part + 1}/{parts}")
        pprint(query)
        if check_avail:
            availability = request_availability(**query)
            print("Availability:")
            jprint(availability)
        data, validation = get_data(**query)
        # It happens that no data is returned without an error code
        # Attempt to get data again if no entry is returned
        n_attempts = 2
        for _ in range(n_attempts):
            if validation["count"]["value"] > 0:
                break
            else:
                time.sleep(1)
                data, validation = get_data(**query)
        print("Validation:")
        jprint(validation)
        print()
        df_list.append(pd.DataFrame.from_dict(data))
        time.sleep(1)
    df = pd.concat(df_list)
    return df
