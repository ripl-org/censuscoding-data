import csv
import gzip
import pandas as pd
import sys

in_files = sys.argv[1:-1]
out_file = sys.argv[-1]

types = {
    "zip": int,
    "street": str,
    "street_num": int,
    "blkgrp": str
}
lookup = pd.concat([pd.read_csv(f, dtype=types) for f in in_files], ignore_index=True)
lookup.sort_values(["zip", "street", "street_num"]).drop_duplicates()

with gzip.open(out_file, "wt") as f:
    writer = csv.writer(f)
    writer.writerow(["zip", "street", "street_num", "blkgrp"])
    n = len(lookup)
    restart = False
    writer.writerow(lookup.iloc[0])
    for i in range(1, n-1):
        # Compress output by skipping redundant numbers
        if (
            (not restart) &
            (lookup.iloc[i]["zip"]    == lookup.iloc[i+1]["zip"]   ) &
            (lookup.iloc[i]["street"] == lookup.iloc[i+1]["street"]) &
            (lookup.iloc[i]["blkgrp"] == lookup.iloc[i+1]["blkgrp"])
        ):
            restart = False
            continue
        writer.writerow(lookup.iloc[i])
        restart = True
    writer.writerow(lookup.iloc[n-1])
