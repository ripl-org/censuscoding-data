import address
import csv
import pandas as pd
import sys

sites_file, out_file = sys.argv[1:]

# Don't use ALIAS5 because it frequently contains a datetime values!
columns = ["GPSX", "GPSY", "ZIP", "HOUSE_NUMBER", "PRIMARYNAME", "ALIAS1", "ALIAS2", "ALIAS3", "ALIAS4"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "GPSX": "X",
            "GPSY": "Y",
            "ZIP": "Zip",
            "HOUSE_NUMBER": "StreetNum"
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
        value_vars=["PRIMARYNAME", "ALIAS1", "ALIAS2", "ALIAS3", "ALIAS4"]
    ).rename(
        columns={
            "value": "StreetName"
        }
    ).dropna()
    .reset_index()
)

with open(out_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
    for record in sites.itertuples():
        StreetName = address.normalize(f"{record.StreetNum} {record.StreetName}")
        if StreetName is not None:
            writer.writerow((record.X, record.Y, record.StreetNum, StreetName, record.Zip))
