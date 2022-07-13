import csv
import gzip
import pandas as pd
import sys
from address import transliterate

sites_file, out_file = sys.argv[1:]

columns = ["Address Number", "Street Name", "ZIP Code", "Longitude", "Latitude"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "Longitude": "X",
            "Latitude": "Y",
            "ZIP Code": "Zip",
            "Address Number": "StreetNum",
            "Street Name": "StreetName"
        }
    )
)

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
