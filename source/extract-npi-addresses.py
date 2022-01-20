import pandas as pd
import sys

npi_file, pl_file, out_file = sys.argv[1:]

npi_columns = {
    "NPI": "npi",
    "Provider First Line Business Practice Location Address": "address",
    "Provider Business Practice Location Address Postal Code": "zip5",
    "Last Update Date": "year"
}

pl_columns = {
    "NPI": "npi",
    "Provider Secondary Practice Location Address- Address Line 1": "address",
    "Provider Secondary Practice Location Address - Postal Code": "zip5"
}


npi = pd.read_csv(npi_file, usecols=npi_columns.keys(), dtype=str).rename(columns=npi_columns)
npi.loc[:,"year"] = npi.year.str.slice(6, 10)
years = npi.loc[npi.year.notnull(), ["npi", "year"]]
del npi["year"]

pl = pd.read_csv(pl_file, usecols=pl_columns.keys(), dtype=str).rename(columns=pl_columns)

addresses = pd.concat([npi, pl], ignore_index=True).merge(years, how="left", on="npi")
addresses.loc[:,"zip5"] = addresses.zip5.str.slice(0, 5)
addresses.dropna(how="any").drop_duplicates().to_csv(out_file, index=False)
