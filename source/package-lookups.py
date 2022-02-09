import gzip
import json
import os
import pickle
import sys
from collections import defaultdict

lookup_file, out_file = sys.argv[1:]

out_dir = os.path.splitext(out_file)[0]
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

print("Reading lookup")
with gzip.open(lookup_file, "rt", encoding="ascii") as f:
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

with open(out_file, "w") as f:
    for zz in packaged:
        print(zz, file=f)
