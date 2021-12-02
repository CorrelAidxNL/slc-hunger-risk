from pathlib import Path
import inspect


def project_dir(*path):
    root = Path(inspect.getframeinfo(inspect.currentframe()).filename).resolve().parents[2]
    return Path(root, *path)

def data_dir(*path):
    return project_dir("data", *path)

def plot_dir(*path):
    return project_dir("plots", *path)


dtype_fao = {
    "Area Code": "Int64", 
    "Item Code": "Int64", 
    "Months Code": "Int64", 
    "Year Code": "Int64", 
    "Element Code": "Int64", 
    "Reporter Country Code": "Int64",
    "Partner Country Code": "Int64",
    "Area": str,
    "Item": str,
    "Months": str,
    "Year": str,
    "Unit": str,
    "Flag": str,
    "Note": str,
    "Element": str,
    "Reporter Countries": str,
    "Partner Countries": str,
    "Value": str,
}