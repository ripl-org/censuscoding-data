import pandas as pd
import sys

npi_file, pl_file, out_file = sys.argv[1:]

npi_columns = {
    "NPI": "record_id",
    "Provider First Line Business Practice Location Address": "address",
    "Provider Business Practice Location Address Postal Code": "zip_code",
    "Last Update Date": "year"
}

pl_columns = {
    "NPI": "record_id",
    "Provider Secondary Practice Location Address- Address Line 1": "address",
    "Provider Secondary Practice Location Address - Postal Code": "zip_code"
}


npi = pd.read_csv(npi_file, usecols=npi_columns.keys(), dtype=str).rename(columns=npi_columns)
npi.loc[:,"year"] = npi.year.str.slice(6, 10)
years = npi.loc[npi.year.notnull(), ["record_id", "year"]]
del npi["year"]

pl = pd.read_csv(pl_file, usecols=pl_columns.keys(), dtype=str).rename(columns=pl_columns)

addresses = pd.concat([npi, pl], ignore_index=True).merge(years, how="left", on="record_id")
print(len(addresses), "total records")

addresses.loc[:,"zip_code"] = addresses.zip_code.str.slice(0, 5)
addresses = addresses.dropna(how="any")
print(len(addresses), "complete records")

addresses = addresses.drop_duplicates(["address", "zip_code", "year"])
print(len(addresses), "distinct records")

addresses.to_csv(out_file, index=False)
