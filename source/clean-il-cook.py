import csv
import gzip
import pandas as pd
import re
import sys
from address import extract_street_num, normalize_street

sites_file, out_file = sys.argv[1:]

re_num = re.compile(r"^([1-9][0-9]*)")

columns = ["longitude", "latitude", "property_address", "property_zip"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "longitude": "X",
            "latitude": "Y",
            "property_zip": "Zip"
        }
    )
)

sites.loc[:, "Zip"] = sites.Zip.str[:5]

# Retain sites with known lat/lon, zip and house number
sites = sites[
    sites.X.notnull() &
    sites.Y.notnull() &
    sites.Zip.notnull() &
    sites.property_address.notnull()
]

with gzip.open(out_file, "wt", encoding="ascii") as f:
    writer = csv.writer(f)
    writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
    for record in sites.itertuples():
        StreetNum = re_num.match(extract_street_num(record.property_address)) # Remove letters in house number
        StreetName = normalize_street(record.property_address)
        if StreetName and StreetNum is not None:
            writer.writerow((record.X, record.Y, StreetNum.group(1), StreetName, record.Zip))
