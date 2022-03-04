import csv
import gzip
import pandas as pd
import sys
from source.address import normalize_street

sites_file, out_file = sys.argv[1:]

columns = ["X", "Y", "Post_Code", "Add_Number", "St_Full", "St_Alias1", "St_Alias2", "St_Alias3", "St_Alias4", "St_Alias5"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "Post_Code": "Zip",
            "Add_Number": "StreetNum"
        }
    )
)

# Retain sites with known lat/lon, zip and house number
sites = sites[
    sites.X.notnull() &
    sites.Y.notnull() &
    sites.Zip.notnull() &
    sites.StreetNum.notnull() &
    (sites.StreetNum != "0")
]

# Melt and remove empty addresses
sites = (
    pd.melt(
        sites,
        id_vars=["X", "Y", "Zip", "StreetNum"], 
        value_vars=["St_Full", "St_Alias1", "St_Alias2", "St_Alias3", "St_Alias4", "St_Alias5"]
    ).rename(
        columns={
            "value": "StreetName"
        }
    ).dropna()
    .reset_index()
)

with gzip.open(out_file, "wt", encoding="ascii") as f:
    writer = csv.writer(f)
    writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
    for record in sites.itertuples():
        StreetName = normalize_street(f"{record.StreetNum} {record.StreetName}")
        if StreetName is not None:
            writer.writerow((record.X, record.Y, record.StreetNum, StreetName, record.Zip))
