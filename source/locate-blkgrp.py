import numpy as np
import pandas as pd
import rtree
import shapefile
import sys
from shapely.geometry import shape, Point

blkgrp_file, address_file, out_file = sys.argv[1:]

# Load and index blockgroup shapes
shapes = {}
geoids = {}
shape_index = rtree.index.Index()
blkgrp = shapefile.Reader(blkgrp_file)
for i in range(len(blkgrp)):
    geoids[i] = blkgrp.record(i)["GEOID"]
    shapes[i] = shape(blkgrp.shape(i))
    shape_index.insert(i, shapes[i].bounds)

# Load lat/lon
address = pd.read_csv(address_file, dtype=str)

# Locate blockgroup for lat/lon
def locate(row):
    p = Point(float(row.X), float(row.Y))
    for i in shape_index.intersection(p.bounds):
        if p.intersects(shapes[i]):
            return geoids[i]
    return np.nan

address["BlockGroup"] = address.apply(locate, axis=1)
address = address[["StreetNum", "StreetName", "Zip", "BlockGroup"]].drop_duplicates()

print("Blockgroup missing for", address.BlockGroup.isnull().sum())
print("Unique blockgroups:", len(address.BlockGroup.unique()))

address.to_csv(out_file, index=False)
