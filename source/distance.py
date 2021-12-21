import numpy as np
import pandas as pd
import sys

xyfile, outfile = sys.argv[1:]

xy = pd.read_csv(xyfile)

with open(outfile, "w") as f:
    print("GEOID1", "GEOID2", "DISTANCE", sep=",", file=f)
    for local in xy.itertuples():
        neighbors = xy[["GEOID", "X", "Y"]].set_index("GEOID")
        # Compute pairwise distance to the neighboring centroids
        neighbors["DISTANCE"] = np.sqrt((neighbors.X - local.X) ** 2 + \
                                        (neighbors.Y - local.Y) ** 2)
        # Use the radius as the within region distance
        neighbors.loc[local.GEOID, "DISTANCE"] = local.RADIUS
        for row in neighbors.itertuples():
            print(local.GEOID, row.Index, 0.001*row.DISTANCE, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
