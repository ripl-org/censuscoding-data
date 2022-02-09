import csv
import gzip
import json
import sys
from collections import defaultdict

in_files = sys.argv[1:-1]
out_file = sys.argv[-1]

lookup = defaultdict(dict)

for in_file in in_files:
    print(in_file)
    with gzip.open(in_file, "rt", encoding="ascii") as f:
        reader = csv.DictReader(f)
        for record in reader:
            lookup[int(record["zip"])][record["street"]] = record["blkgrp"]

print("Writing output")
with gzip.open(out_file, "wt", encoding="ascii") as f:
    json.dump(lookup, f)
