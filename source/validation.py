import gzip
import json
import numpy as np
import os
import pandas as pd
from zipfile import ZipFile

from source.utils import BlockGroupIndex


def _extract_cms_npi(zip_file, blkgrp_file, out_file):
    """
    """
    npi_columns = {
        "NPI": "record_id",
        "Provider First Line Business Practice Location Address": "address",
        "Provider Business Practice Location Address Postal Code": "zipcode",
        "Last Update Date": "year"
    }

    pl_columns = {
        "NPI": "record_id",
        "Provider Secondary Practice Location Address- Address Line 1": "address",
        "Provider Secondary Practice Location Address - Postal Code": "zipcode"
    }

    with ZipFile(zip_file) as z:
        with z.open("Validation/CMS-NPI/20211214/npidata_pfile_20050523-20211212.csv.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                npi = pd.read_csv(g, usecols=npi_columns.keys(), dtype=str).rename(columns=npi_columns)
        with z.open("Validation/CMS-NPI/20211214/pl_pfile_20050523-20211212.csv.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                pl = pd.read_csv(g, usecols=pl_columns.keys(), dtype=str).rename(columns=pl_columns)

    npi.loc[:,"year"] = npi.year.str.slice(6, 10)
    years = npi.loc[npi.year.notnull(), ["record_id", "year"]]
    del npi["year"]

    addresses = pd.concat([npi, pl], ignore_index=True).merge(years, how="left", on="record_id")
    print(len(addresses), "total records")

    addresses.loc[:,"zipcode"] = addresses.zipcode.str.slice(0, 5)
    addresses = addresses.dropna(how="any")
    print(len(addresses), "complete records")

    addresses = addresses.drop_duplicates(["address", "zipcode", "year"])
    print(len(addresses), "distinct records")

    addresses.to_csv(out_file, index=False)


def _extract_epa_frs(zip_file, blkgrp_file, out_file):
    """
    """
    with ZipFile(zip_file) as z:
        with z.open("Validation/EPA-FRS/20220711/NATIONAL_SINGLE.CSV.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                data = pd.read_csv(
                    g,
                    usecols=[
                        "REGISTRY_ID",
                        "LOCATION_ADDRESS",
                        "POSTAL_CODE",
                        "CENSUS_BLOCK_CODE",
                        "LONGITUDE83",
                        "LATITUDE83",
                        "CREATE_DATE"
                    ],
                    dtype=str
                ).rename(
                    columns={
                        "REGISTRY_ID": "record_id",
                        "LOCATION_ADDRESS": "address",
                        "POSTAL_CODE": "zipcode",
                        "LONGITUDE83": "X",
                        "LATITUDE83": "Y"
                    }
                ).dropna()

    index = BlockGroupIndex(blkgrp_file)

    print("Found", len(data), "records")

    def roll_year(date):
        yy = int(date[7:9])
        if yy > 22:
            return 1900 + yy
        else:
            return 2000 + yy

    data["year"] = data.CREATE_DATE.apply(roll_year)

    data = data[data.X.notnull() & data.Y.notnull()]

    print("Kept", len(data), "records with lat/lon")

    data["blkgrp_true"] = data.apply(lambda row: index.locate(row.X, row.Y), axis=1)

    print("blkgrp success rate:", data["blkgrp_true"].notnull().sum() / len(data))
    print("existing blkgrp:", data.CENSUS_BLOCK_CODE.notnull().sum() / len(data))
    print("blkgrp agreement:", (data["blkgrp_true"] == data.CENSUS_BLOCK_CODE.str[:12]).sum() / len(data))

    data[["record_id", "address", "zipcode", "year", "blkgrp_true"]].to_csv(out_file, index=False)


def _extract_hud_phb(zip_file, blkgrp_file, out_file):
    """
    """
    with ZipFile(zip_file) as z:
        with z.open("Validation/HUD-PHB/20220711/Public_Housing_Buildings.csv") as f:
            data = pd.read_csv(
                f,
                usecols=["OBJECTID", "STD_ADDR", "STD_ZIP5", "BLKGRP_LEVEL", "LAT", "LON", "CONSTRUCT_DATE"],
                dtype=str
            ).rename(
                columns={
                    "OBJECTID": "record_id",
                    "STD_ADDR": "address",
                    "STD_ZIP5": "zipcode",
                    "LON": "X",
                    "LAT": "Y"
                }
            )

    index = BlockGroupIndex(blkgrp_file)

    print("Found", len(data), "records")

    data["year"] = data.CONSTRUCT_DATE.str[:4]

    data = data[data.X.notnull() & data.Y.notnull()]

    print("Kept", len(data), "records with lat/lon")

    data["blkgrp_true"] = data.apply(lambda row: index.locate(row.X, row.Y), axis=1)

    print("blkgrp success rate:", data["blkgrp_true"].notnull().sum() / len(data))
    print("existing blkgrp:", data.BLKGRP_LEVEL.notnull().sum() / len(data))
    print("blkgrp agreement:", (data["blkgrp_true"] == data.BLKGRP_LEVEL.str[:12]).sum() / len(data))

    data[["record_id", "address", "zipcode", "year", "blkgrp_true"]].dropna().to_csv(out_file, index=False)


def _extract_uspto_pat(zip_file, blkgrp_file, out_file):
    """
    """
    with ZipFile(zip_file) as z:
        with z.open("Validation/USPTO-Patent/2020/assignment.csv.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                years = (
                    pd.read_csv(g, usecols=["rf_id", "record_dt"], dtype=str)
                      .dropna(how="any")
                      .rename(columns={"rf_id": "record_id"})
                )
        with z.open("Validation/USPTO-Patent/2020/assignee.csv.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                columns = {
                    "rf_id": "record_id",
                    "ee_address_1": "address1",
                    "ee_address_2": "address2",
                    "ee_postcode": "zipcode",
                    "ee_country": "country"
                }
                addresses = pd.read_csv(g, usecols=columns.keys(), dtype=str).rename(columns=columns)
                print(len(addresses), "total records")

    years.loc[:,"year"] = years.record_dt.str.slice(0, 4)
    del years["record_dt"]
    years = years.groupby("record_id").min().reset_index()

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


def _extract_uspto_tm(zip_file, blkgrp_file, out_file):
    """
    """
    with ZipFile(zip_file) as z:
        with z.open("Validation/USPTO-Trademark/2020/tm_assignment.csv.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                years = (
                    pd.read_csv(g, usecols=["rf_id", "record_dt"], dtype=str)
                      .dropna(how="any")
                      .rename(columns={"rf_id": "record_id"})
                )
        with z.open("Validation/USPTO-Trademark/2020/tm_assignee.csv.gz") as f:
            with gzip.GzipFile(fileobj=f, mode="rb") as g:
                columns = {
                    "rf_id": "record_id",
                    "ee_address_1": "address1",
                    "ee_address_2": "address2",
                    "ee_postcode": "zipcode",
                    "ee_country": "country"
                }
                addresses = pd.read_csv(g, usecols=columns.keys(), dtype=str).rename(columns=columns)
                print(len(addresses), "total records")

    years.loc[:,"year"] = years.record_dt.str.slice(0, 4)
    del years["record_dt"]
    years = years.groupby("record_id").min().reset_index()

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


_extract_funcs = {
    "cms-npi": _extract_cms_npi,
    "epa-frs": _extract_epa_frs,
    "hud-phb": _extract_hud_phb,
    "uspto-pat": _extract_uspto_pat,
    "uspto-tm": _extract_uspto_tm
}


def Extract(target, source, env):
    """
    Extract each test set and normalize its columns.
    source[0]: (test name)
    source[1]: Validation.zip
    source[2]: national-blkgrp.pickle
    """
    test = source[0].value
    _extract_funcs[test](source[1].path, source[2].path, target[0].path)


def Coverage(target, source, env):
    """
    Determine the fraction of test addresses that were successfully
    censuscoded to some blockgroup.
    source[0]: zip3.csv
    source[1:]: (censuscoded test files)
    """
    zip3 = frozenset(pd.read_csv(source[0].path, dtype=str).zip3)

    def coverage_by_zip_year(infile):
        tokens = os.path.splitext(infile)[0].split(os.sep)
        test = tokens[-1]
        lookup = tokens[-2]
        df = pd.read_csv(infile, dtype=str)
        df = df[df.pobox.isnull() & df.unsheltered.isnull() & df.zipcode.str[:3].isin(zip3)]
        df["n"] = 1
        df["blkgrp"] = df["blkgrp"].notnull().astype(int)
        df = df.groupby(["zipcode", "year"])[["blkgrp", "n"]].sum().reset_index()
        df["test"] = test
        df["lookup"] = lookup
        return df

    pd.concat(
        [
            coverage_by_zip_year(s.path)
            for s in source[1:]
        ],
        ignore_index=True
    ).to_csv(target[0].path, index=False)


def Accuracy(target, source, env):
    """
    Determine the fraction of test addresses that were successfully
    censuscoded to the correct blockgroup.
    source: (censuscoded test files)
    """
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
            accuracy_by_zip_year(s.path)
            for s in source
        ],
        ignore_index=True
    ).to_csv(target[0].path, index=False)
