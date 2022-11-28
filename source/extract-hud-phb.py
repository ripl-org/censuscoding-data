import numpy as np
import pandas as pd
import rtree
import sys
from shapely.geometry import shape, Point

in_file, blkgrp_file, out_file = sys.argv[1:]

blkgrp = rtree.index.Index(blkgrp_file.rpartition(".")[0])

data = pd.read_csv(
    in_file,
    usecols=["OBJECTID", "STD_ADDR", "STD_ZIP5", "BLKGRP_LEVEL", "LAT", "LON", "CONSTRUCT_DATE"],
    dtype=str
).rename(
    columns={
        "OBJECTID": "record_id",
        "STD_ADDR": "address",
        "STD_ZIP5": "zipcode",
        "LON": "X",
        "LAT": "Y"
    }
)

print("Found", len(data), "records")

data["year"] = data.CONSTRUCT_DATE.str[:4]

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
print("existing blkgrp:", data.BLKGRP_LEVEL.notnull().sum() / len(data))
print("blkgrp agreement:", (data["blkgrp_true"] == data.BLKGRP_LEVEL.str[:12]).sum() / len(data))

data[["record_id", "address", "zipcode", "year", "blkgrp_true"]].dropna().to_csv(out_file, index=False)
