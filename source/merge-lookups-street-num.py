import csv
import json
import gzip
import sys
from bisect import bisect_left

street_file = sys.argv[1]
in_files = sys.argv[2:-1]
out_file = sys.argv[-1]

with gzip.open(street_file, "rt", encoding="ascii") as f:
    lookup = json.load(f)

for in_file in in_files:
    print(in_file)
    with gzip.open(in_file, "rt", encoding="ascii") as f:
        reader = csv.DictReader(f)
        for record in reader:
            z = int(record["zip"])
            n = int(record["street_num"])

            # Add this zipcode to the lookup if there was no street entry.
            if z not in lookup:
                lookup[z] = {}

            # Update an existing record for this street
            if record["street"] in lookup[z]:
                # Make sure this street is a numbered street
                assert isinstance(lookup[z][record["street"]], list), f"{record['zip']}:{record['street']}"
                nums = lookup[z][record["street"]][0]
                blkgrps = lookup[z][record["street"]][1]
                # Binary search to locate index for street_num.
                i = bisect_left(nums, n)
                # Merge street_num with neighboring street_num if they share
                # the same blockgroup.
                if i < len(nums) and blkgrps[i] == record["blkgrp"]:
                    nums[i] = n
                elif i > 0 and blkgrps[i-1] == record["blkgrp"]:
                    nums[i-1] = n
                else:
                    nums.insert(i, n)
                    blkgrps.insert(i, record["blkgrp"])
            # Or create a new record for this street
            else:
                lookup[z][record["street"]] = [[n], [record["blkgrp"]]]

print("Writing output")
with gzip.open(out_file, "wt", encoding="ascii") as f:
    json.dump(lookup, f)
