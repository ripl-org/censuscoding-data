import csv
import gzip
import pandas as pd
import re
import sys
from address import transliterate

sites_file, out_file = sys.argv[1:]

re_num = re.compile(r"^([1-9][0-9]*)")

columns = ["ADDR_HN", "ADDR_PD", "ADDR_SN", "ZIP5", "LAT", "LON"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "LON": "X",
            "LAT": "Y",
            "ZIP5": "Zip",
            "ADDR_HN": "StreetNum"
        }
    )
)

# Street prefix
sites.loc[:, "StreetName"] = (sites.ADDR_PD.fillna("") + " " + sites.ADDR_SN).str.lstrip(" ")

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
        StreetNum = re_num.match(record.StreetNum) # Remove letters in house number
        StreetName = transliterate(record.StreetName)
        if StreetNum is not None:
            writer.writerow((record.X, record.Y, StreetNum.group(1), StreetName, record.Zip))
