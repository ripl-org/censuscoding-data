import numpy as np
import pandas as pd
import rtree
import sys
from shapely.geometry import shape, Point

in_file, blkgrp_file, out_file = sys.argv[1:]

blkgrp = rtree.index.Index(blkgrp_file.rpartition(".")[0])

data = pd.read_csv(
    in_file,
    usecols=["REGISTRY_ID", "LOCATION_ADDRESS", "POSTAL_CODE", "CENSUS_BLOCK_CODE", "LONGITUDE83", "LATITUDE83", "CREATE_DATE"],
    dtype=str
).rename(
    columns={
        "REGISTRY_ID": "record_id",
        "LOCATION_ADDRESS": "address",
        "POSTAL_CODE": "zipcode",
        "LONGITUDE83": "X",
        "LATITUDE83": "Y"
    }
).dropna()

print("Found", len(data), "records")

def roll_year(date):
    yy = int(date[7:9])
    if yy > 22:
        return 1900 + yy
    else:
        return 2000 + yy

data["year"] = data.CREATE_DATE.apply(roll_year)

data = data[data.X.notnull() & data.Y.notnull()]

print("Kept", len(data), "records with lat/lon")

# Locate blockgroup for lat/lon
def locate(row):
    p = Point(float(row.X), float(row.Y))
    for match in blkgrp.intersection(p.bounds, "raw"):
        if p.intersects(match["shape"]):
            return match["geoid"]
    return np.nan

data["blkgrp_true"] = data.apply(locate, axis=1)

print("blkgrp success rate:", data["blkgrp_true"].notnull().sum() / len(data))
print("existing blkgrp:", data.CENSUS_BLOCK_CODE.notnull().sum() / len(data))
print("blkgrp agreement:", (data["blkgrp_true"] == data.CENSUS_BLOCK_CODE.str[:12]).sum() / len(data))

data[["record_id", "address", "zipcode", "year", "blkgrp_true"]].to_csv(out_file, index=False)
