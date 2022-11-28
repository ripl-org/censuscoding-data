import rtree
import shapefile
import sys
from shapely.geometry import shape

in_files = sys.argv[1:-1]
out_file = sys.argv[-1].rpartition(".")[0]

print("Found", len(in_files), "input shapefiles")

# Load and index blockgroup shapes
shape_index = rtree.index.Index(out_file)
n = 0
for in_file in in_files:
    blkgrp = shapefile.Reader(in_file)
    for i in range(len(blkgrp)):
        s = shape(blkgrp.shape(i))
        shape_index.insert(
            n,
            s.bounds,
            {
                "geoid": blkgrp.record(i)["GEOID"],
                "shape": s
            }
        )
        n += 1

print("Saving", n, "records to shape index")

shape_index.close()
