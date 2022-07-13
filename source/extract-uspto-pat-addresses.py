import pandas as pd
import numpy as np
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
    "ee_address_1": "address1",
    "ee_address_2": "address2",
    "ee_postcode": "zipcode",
    "ee_country": "country"
}

addresses = pd.read_csv(assignee_file, usecols=columns.keys(), dtype=str).rename(columns=columns)
print(len(addresses), "total records")

addresses = addresses[addresses.country.isnull()] # US addresses have empty country
del addresses["country"]
print(len(addresses), "US records")

# Remove corporation titles from address fields
addresses.loc[addresses.address1.notnull() & addresses.address1.str.startswith("A "), "address1"] = np.nan
addresses.loc[addresses.address2.notnull() & addresses.address2.str.startswith("A "), "address2"] = np.nan

# Fill missing address1 with address2
missing1 = addresses.address1.isnull()
addresses.loc[missing1, "address1"] = addresses.loc[missing1, "address2"]
print(sum(missing1), "missing address1")

addresses.rename(columns={"address1": "address"}, inplace=True)
del addresses["address2"]

addresses = addresses.dropna(how="any")
print(len(addresses), "complete records")

addresses.loc[:,"zipcode"] = addresses.zipcode.str.slice(0, 5)
addresses = addresses.merge(years, how="left", on="record_id").drop_duplicates(["address", "zipcode", "year"])
print(len(addresses), "distinct records")

addresses.to_csv(out_file, index=False)
