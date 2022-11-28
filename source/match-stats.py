import pandas as pd
import sys

in_file, out_file = sys.argv[1:]

data = pd.read_csv(in_file, usecols=["blkgrp", "blkgrp_true", "year"], dtype=str)

print(len(data), "records")
print(data.blkgrp.notnull().sum(), "matches")

matchable = data.blkgrp.notnull() & data.blkgrp_true.notnull()

exact = (data.loc[matchable, "blkgrp"] == data.loc[matchable, "blkgrp_true"]).sum()
print(exact, "correct exact matches")

tract = (data.loc[matchable, "blkgrp"].str[:11] == data.loc[matchable, "blkgrp_true"].str[:11]).sum()
print(tract, "correct tract-level matches")

county = (data.loc[matchable, "blkgrp"].str[:5] == data.loc[matchable, "blkgrp_true"].str[:5]).sum()
print(county, "correct county-level matches")
