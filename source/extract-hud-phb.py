import pandas as pd
import sys

in_file, out_file = sys.argv[1:]

data = pd.read_csv(
    in_file,
    usecols=["OBJECTID", "STD_ADDR", "STD_ZIP5", "BLKGRP_LEVEL", "CONSTRUCT_DATE"],
    dtype=str
).rename(
    columns={
        "OBJECTID": "record_id",
        "STD_ADDR": "address",
        "STD_ZIP5": "zipcode",
        "BLKGRP_LEVEL": "blkgrp_true"
    }
)

data["year"] = data.CONSTRUCT_DATE.str[:4]

data[["record_id", "address", "zipcode", "year", "blkgrp_true"]].dropna().to_csv(out_file, index=False)
