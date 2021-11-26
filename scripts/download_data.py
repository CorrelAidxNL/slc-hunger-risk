from io import BytesIO
import os
import pandas as pd
import requests
from zipfile import ZipFile

from slc_hunger_risk.config import data_dir

country = "Suriname"

### FAOSTAT

# Download
fao_url = r"https://fenixservices.fao.org/faostat/static/bulkdownloads/"

fao_filenames = [    
    "ConsumerPriceIndices_E_All_Data",
    "Food_Security_Data_E_All_Data",
    "FoodBalanceSheets_E_All_Data",
    "Prices_E_All_Data",
    "Trade_CropsLivestock_E_All_Data",
    "Trade_DetailedTradeMatrix_E_All_Data",
    "Value_of_Production_E_All_Data",
]
fao_filenames = [filename + "_(Normalized)" for filename in fao_filenames]

os.makedirs(data_dir("raw", "fao"), exist_ok=True)

for filename in fao_filenames:
    dest = data_dir("raw", "fao", filename + ".csv")
    if dest.exists():
        continue
    url = fao_url + filename + ".zip"
    print(f"Downloading and unzipping {url}")
    r = requests.get(url, stream=True)
    zip_file = ZipFile(BytesIO(r.content))
    extracted_name = zip_file.namelist()[0]
    zip_file.extractall(path=dest.parent)
    os.rename(data_dir("raw", "fao", extracted_name), dest)

# Filter and save
dest = data_dir("processed", f"fao-data-{country}.csv")
if not dest.exists():
    dfs = []
    for filename in fao_filenames:
        file = data_dir("raw", "fao", filename + ".csv")
        with pd.read_csv(file, chunksize=1e6, encoding="latin-1", dtype="string") as reader:
            for df in reader:
                area_filter = (df["Area"] == country) if "Area" in df.columns else False
                reporter_partner_filter =  (((df["Reporter Countries"] == country ) | (df["Partner Countries"] == country)) 
                    if "Reporter Countries" in df.columns else False)
                df = df[area_filter | reporter_partner_filter]
                dfs.append(df)
    df = pd.concat(dfs)

    df.to_csv(data_dir("processed", f"fao-data-{country}.csv"), index=False)


dtype = {
    "Area Code": "Int64", 
    "Item Code": "Int64", 
    "Months Code": "Int64", 
    "Year Code": "Int64", 
    "Element Code": "Int64", 
    "Reporter Country Code": "Int64",
    "Partner Country Code": "Int64",
    "Area": "string",
    "Item": "string",
    "Months": "string",
    "Year": "string",
    "Unit": "string",
    "Flag": "string",
    "Note": "string",
    "Element": "string",
    "Reporter Countries": "string",
    "Partner Countries": "string",
    "Value": "string",
}

df = pd.read_csv(dest, dtype=dtype)

print(df.dtypes)


## IDB

idb_url = r"https://publications.iadb.org/publications/english/document/"

idb_filenames = [
    "Suriname-COVID-19-Survey",
    "Suriname-Survey-of-Living-Conditions-2016-2017"
]

os.makedirs(data_dir("raw", "idb"), exist_ok=True)

if not any(data_dir("raw", "idb").iterdir()):
    for filename in idb_filenames:
        url = idb_url + filename + ".zip"
        print(f"Downloading and unzipping {url}")
        r = requests.get(url, stream=True)
        zip_file = ZipFile(BytesIO(r.content))
        extracted_names = zip_file.namelist()
        zip_file.extractall(path=data_dir("raw", "idb"))
