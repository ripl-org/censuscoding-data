import csv
import gzip
import pandas as pd
import sys
from address import transliterate

sites_file, out_file = sys.argv[1:]

columns = ["X", "Y", "ADDRNMBR", "ADDRPDIR", "ADDRNAME", "ADDRZIP"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str,
        na_values=" "
    ).rename(
        columns={
            "ADDRZIP": "Zip",
            "ADDRNMBR": "StreetNum"
        }
    )
)

# Street prefix
sites.loc[:, "StreetName"] = (sites.ADDRPDIR.fillna("") + " " + sites.ADDRNAME.str.lstrip("0")).str.lstrip(" ")

# Retain sites with known lat/lon, zip and house number
sites = sites[
    sites.X.notnull() &
    sites.Y.notnull() &
    sites.Zip.notnull() &
    sites.StreetNum.notnull() &
    (sites.StreetNum != "0") &
    sites.StreetName.notnull()
]

with gzip.open(out_file, "wt", encoding="ascii") as f:
    writer = csv.writer(f)
    writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
    for record in sites.itertuples():
        StreetName = transliterate(record.StreetName)
        writer.writerow((record.X, record.Y, record.StreetNum, StreetName, record.Zip))
