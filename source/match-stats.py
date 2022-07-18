import pandas as pd
import sys

in_file, out_file = sys.argv[1:]

data = pd.read_csv(in_file, usecols=["blkgrp", "blkgrp_true", "year"], dtype=str)

print(len(data), "records")
print(data.blkgrp.notnull().sum(), "matches")

matchable = data.blkgrp.notnull() & data.blkgrp_true.notnull()
correct = (data.loc[matchable, "blkgrp"] == data.loc[matchable, "blkgrp_true"]).sum()

print(correct, "correct matches")
