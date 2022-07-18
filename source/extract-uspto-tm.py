import pandas as pd
import sys

assignment_file, assignee_file, out_file = sys.argv[1:]

years = (
    pd.read_csv(assignment_file, usecols=["rf_id", "record_dt"], dtype=str)
      .dropna(how="any")
      .rename(columns={"rf_id": "record_id"})
)
years.loc[:,"year"] = years.record_dt.str.slice(0, 4)
del years["record_dt"]
years = years.groupby("record_id").min().reset_index()

columns = {
    "rf_id": "record_id",
    "ee_address_2": "address",
    "ee_postcode": "zipcode",
    "ee_country": "country"
}

addresses = pd.read_csv(assignee_file, usecols=columns.keys(), dtype=str).rename(columns=columns)
print(len(addresses), "total records")

addresses = addresses[addresses.country.isnull()] # US addresses have empty country
del addresses["country"]
print(len(addresses), "US records")

addresses = addresses.dropna(how="any")
print(len(addresses), "complete records")

addresses.loc[:,"zipcode"] = addresses.zipcode.str.slice(0, 5)
addresses = addresses.merge(years, how="left", on="record_id").drop_duplicates(["address", "zipcode", "year"])
print(len(addresses), "distinct records")

addresses.to_csv(out_file, index=False)
