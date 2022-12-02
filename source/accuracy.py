import os
import pandas as pd
import sys

infiles = sys.argv[1:-1]
outfile = sys.argv[-1]

def accuracy_by_zip_year(infile):
    tokens = os.path.splitext(infile)[0].split(os.sep)
    test = tokens[-1]
    lookup = tokens[-2]
    df = pd.read_csv(infile, dtype=str)
    df = df[df.pobox.isnull() & df.unsheltered.isnull() & df.blkgrp.notnull()]
    df["n"] = 1
    df["county_true"] = (df["blkgrp"].str[:5] == df["blkgrp_true"].fillna("").str[:5]).astype(int)
    df["tract_true"] = (df["blkgrp"].str[:11] == df["blkgrp_true"].fillna("").str[:11]).astype(int)
    df["blkgrp_true"] = (df["blkgrp"] == df["blkgrp_true"]).astype(int)
    df = df.groupby(["zipcode", "year"])[["n", "blkgrp_true", "tract_true", "county_true"]].sum().reset_index()
    df["test"] = test
    df["lookup"] = lookup
    return df

pd.concat(
    [
        accuracy_by_zip_year(infile)
        for infile in infiles
    ],
    ignore_index=True
).to_csv(outfile, index=False)
