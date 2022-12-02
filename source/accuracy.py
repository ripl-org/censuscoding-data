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
    df = df[df.pobox.isnull() & df.unsheltered.isnull() & (df.zipcode != "00000")]
    df["blkgrp"] = df["blkgrp"].notnull().astype(int)
    df["blkgrp_true"] = (df["blkgrp"] == df["blkgrp_true"]).astype(int)
    df = df.groupby(["zipcode", "year"])[["blkgrp", "blkgrp_true"]].sum().reset_index()
    df = df[df["blkgrp"] > 0]
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
