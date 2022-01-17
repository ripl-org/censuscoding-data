import csv
import gzip
import json
import sys
from collections import defaultdict

names_file, nums_file, out_file = sys.argv[1:]

lookup = defaultdict(dict)

# Add street names
with gzip.open(names_file, "rt") as f:
    reader = csv.DictReader(f)
    for row in reader:
        lookup[row["zip"]][row["street"]] = row["blkgrp"]

# Add street_num ranges
with gzip.open(nums_file, "rt") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row["street"] in lookup[row["zip"]]:
            lookup[row["zip"]][row["street"]] = [[],[]]
        lookup[row["zip"]][row["street"]][0].append(row["street_num"])
        lookup[row["zip"]][row["street"]][1].append(row["blkgrp"])

# Save as compressed json per zipcode
out_dir = os.path.dirname(out_file)
for zip5 in lookup:
    with gzip.open(os.path.join(out_dir, zip5 + ".json.gz"), "wt") as f:
        json.dump(lookup[zip5], f)
with gzip.open(outfile, "wt") as f:
    json.dump(lookup, f)
