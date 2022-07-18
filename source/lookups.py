import csv
import gzip
import json
import os
import pickle
import sys
from bisect import bisect_left
from collections import defaultdict


def MergeStreet(target, source, env):
    """
    Read multiple street lookups and merge into a single JSON file.
    """
    lookup = defaultdict(dict)
    for street_file in map(str, source):
        with gzip.open(street_file, "rt", encoding="ascii") as f:
            reader = csv.DictReader(f)
            for record in reader:
                lookup[int(record["zip"])][record["street"]] = record["blkgrp"]
    with gzip.open(str(target[0]), "wt", encoding="ascii") as f:
        json.dump(lookup, f)


def MergeStreetNum(target, source, env):
    """
    """
    with gzip.open(str(source[0]), "rt", encoding="ascii") as f:
        lookup = json.load(f)

    for num_file in map(str, source[1:]):
        with gzip.open(num_file, "rt", encoding="ascii") as f:
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

    with gzip.open(str(target[0]), "wt", encoding="ascii") as f:
        json.dump(lookup, f)


def Package(target, source, env):
    """
    """
    out_dir = os.path.splitext(str(target[0]))[0]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with gzip.open(str(source[0]), "rt", encoding="ascii") as f:
        lookup = json.load(f)

    # Pickle at the 2-digit zipcode level

    packaged = defaultdict(dict)
    for z in lookup:
        zip5 = z.zfill(5)
        if zip5 != "00000":
            zz = zip5[:2]
            zzz = zip5[2:]
            packaged[zz][zzz] = lookup[z]

    for zz in packaged:
        path = os.path.join(out_dir, zz)
        with open(path, "wb") as f:
            pickle.dump(packaged[zz], f)

    with open(str(target[0]), "w") as f:
        for zz in packaged:
            print(zz, file=f)
