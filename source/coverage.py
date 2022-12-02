import os
import pandas as pd
import sys

zip3file = sys.argv[1]
infiles  = sys.argv[2:-1]
outfile  = sys.argv[-1]

zip3 = pd.read_csv(zip3file, dtype=str)

def coverage_by_zip_year(infile):
    tokens = os.path.splitext(infile)[0].split(os.sep)
    test = tokens[-1]
    lookup = tokens[-2]
    df = pd.read_csv(infile, dtype=str)
    df = df[df.pobox.isnull() & df.unsheltered.isnull() & df.zipcode.str[:3].isin(zip3.zip3)]
    df["n"] = 1
    df["blkgrp"] = df["blkgrp"].notnull().astype(int)
    df = df.groupby(["zipcode", "year"])[["blkgrp", "n"]].sum().reset_index()
    df["test"] = test
    df["lookup"] = lookup
    return df

pd.concat(
    [
        coverage_by_zip_year(infile)
        for infile in infiles
    ],
    ignore_index=True
).to_csv(outfile, index=False)
