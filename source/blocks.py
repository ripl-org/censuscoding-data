import fiona
import numpy as np
import pandas as pd
import rtree
import sys
from shapely.geometry import shape, Point

blk_shapefile, csvfile, outfile = sys.argv[1:]

# Load and index block shapes
blk_shapes = {}
geoids = {}
blk_index = rtree.index.Index()
for block in fiona.open(blk_shapefile, "r"):
    i = int(block["id"])
    blk_shapes[i] = shape(block["geometry"])
    geoids[i] = str(block["properties"]["GEOID20"])
    blk_index.insert(i, blk_shapes[i].bounds)

# Load lat/lon
df = pd.read_csv(csvfile, low_memory=False)

# Locate block for lat/lon
def locate_blk(row):
    p = Point(row.X, row.Y)
    for j in blk_index.intersection(p.bounds):
        if p.intersects(blk_shapes[j]):
            return geoids[j]
    return np.nan

# Locate block for lat/lon
def locate_zip(row):
    p = Point(row.X, row.Y)
    for j in zip_index.intersection(p.bounds):
        if p.intersects(zip_shapes[j]):
            return zip_codes[j]
    return np.nan

df["Block"] = df.apply(locate_blk, axis=1)

final = df[["StreetNum", "StreetName", "StreetType", "City", "Zip", "Block"]].drop_duplicates()
final["BlockGroup"] = final.Block.astype(str).str.slice(0, 12)
final["Tract"] = final.Block.astype(str).str.slice(0, 11)

print("Block missing for", final.Block.isnull().sum())
print("Unique blocks:", len(final.Block.unique()))
print("Unique blockgroups:", len(final.BlockGroup.unique()))
print("Unique tracts:", len(final.Tract.unique()))

final.to_csv(outfile, index=False, float_format="%g")

