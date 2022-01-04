import address
import csv
import gzip
import pandas as pd
import sys

sites_file, out_file = sys.argv[1:]

# Don't use ALIAS5 because it frequently contains a datetime values!
columns = ["LONGITUDE", "LATITUDE", "ZIPCODE", "ADDRESS_NUMBER", "RDNAME"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "LONGITUDE": "X",
            "LATITUDE": "Y",
            "ZIPCODE": "Zip",
            "ADDRESS_NUMBER": "StreetNum",
            "RDNAME": "StreetName"
        }
    )
)

# Retain sites with known distinct lat/lon, zip and house number
sites = sites[
    sites.X.notnull() &
    sites.Y.notnull() &
    (sites.X != sites.Y) &
    sites.Zip.notnull() &
    sites.StreetNum.notnull() &
    (sites.StreetNum != "0")
]

with gzip.open(out_file, "wt") as f:
    writer = csv.writer(f)
    writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
    for record in sites.itertuples():
        StreetName = address.normalize(f"{record.StreetNum} {record.StreetName}")
        if StreetName is not None:
            writer.writerow((record.X, record.Y, record.StreetNum, StreetName, record.Zip))
