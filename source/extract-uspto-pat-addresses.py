import pandas as pd
import sys

assignment_file, assignee_file, out_file = sys.argv[1:]

years = pd.read_csv(assignment_file, usecols=["rf_id", "record_dt"], dtype=str).dropna(how="any")
years.loc[:,"year"] = years.record_dt.str.slice(0, 4)
del years["record_dt"]
years = years.groupby("rf_id").min().reset_index()
print(years)

columns = {
    "rf_id": "rf_id",
    "ee_address_2": "address",
    "ee_postcode": "zip5",
    "ee_country": "country"
}

addresses = pd.read_csv(assignee_file, usecols=columns.keys(), dtype=str).rename(columns=columns)
addresses = addresses[addresses.country.isnull()] # US addresses have empty country
del addresses["country"]
addresses.loc[:,"zip5"] = addresses.zip5.str.slice(0, 5)
addresses.dropna(how="any").merge(years, how="left", on="rf_id").drop_duplicates().to_csv(out_file, index=False)
