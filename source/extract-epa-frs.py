import pandas as pd
import sys

in_file, out_file = sys.argv[1:]

data = pd.read_csv(
    in_file,
    usecols=["REGISTRY_ID", "LOCATION_ADDRESS", "POSTAL_CODE", "CENSUS_BLOCK_CODE", "CREATE_DATE"],
    dtype=str
).rename(
    columns={
        "REGISTRY_ID": "record_id",
        "LOCATION_ADDRESS": "address",
        "POSTAL_CODE": "zipcode"
    }
).dropna()

data["blkgrp_true"] = data.CENSUS_BLOCK_CODE.str[:12]

def roll_year(date):
    yy = int(date[7:9])
    if yy > 22:
        return 1900 + yy
    else:
        return 2000 + yy

data["year"] = data.CREATE_DATE.apply(roll_year)

data[["record_id", "address", "zipcode", "year", "blkgrp_true"]].to_csv(out_file, index=False)
