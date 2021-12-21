import fiona
import math
import pyproj
import sys
from functools import partial
from shapely.geometry import shape
from shapely.ops import transform

shapefile, outfile = sys.argv[1:]

proj = partial(pyproj.transform,
               pyproj.Proj('EPSG:4326'),
               pyproj.Proj('EPSG:32633'))

with open(outfile, "w") as f:
    print("GEOID", "LON", "LAT", "X", "Y", "RADIUS", sep=",", file=f)
    for s in fiona.open(shapefile, "r"):
        geoid = s["properties"]["GEOID"]
        s = shape(s["geometry"])
        t = transform(proj, s)
        print(geoid,
              s.centroid.x,
              s.centroid.y,
              t.centroid.x,
              t.centroid.y,
              math.sqrt(t.area/math.pi),
              sep=",",
              file=f)

# vim: syntax=python expandtab sw=4 ts=4
