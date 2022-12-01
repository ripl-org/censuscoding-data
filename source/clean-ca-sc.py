import csv
import gzip
import pandas as pd
import re
import sys
from address import transliterate

sites_file, out_file = sys.argv[1:]

re_point = re.compile(r"^POINT \(([\-\.\d]+) ([\-\.\d]+)\)$")
re_num   = re.compile(r"^([1-9][0-9]*)")

columns = ["the_geom", "HOUSENUMTEXT", "STREETPREFIX", "STREETNAME", "ZIPCODE"]

sites = (
    pd.read_csv(
        sites_file,
        usecols=columns,
        dtype=str
    ).rename(
        columns={
            "ZIPCODE": "Zip",
            "HOUSENUMTEXT": "StreetNum"
        }
    )
)

# Split POINT entry into seperate X and Y
def split_point(p, n=0):
    match = re_point.match(p)
    if match is not None:
        return match.group(n)
    return ""
sites.loc[:, "X"] = sites.the_geom.apply(split_point, n=1)
sites.loc[:, "Y"] = sites.the_geom.apply(split_point, n=2)

# Street prefix
sites.loc[:, "StreetName"] = (sites.STREETPREFIX.fillna("") + " " + sites.STREETNAME).str.lstrip(" ")

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
