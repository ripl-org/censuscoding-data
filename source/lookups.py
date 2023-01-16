import csv
import gzip
import json
import os
import pandas as pd
import pickle
import shapefile
import sys
from itertools import groupby
from operator import attrgetter

from source.address import normalize_street
from source.utils import open_files, close_files, BlockGroupIndex


header = ["StreetNum", "StreetName", "Zip", "BlockGroup"]


def NationalBlockGroups(target, source, env):
    """
    Combine all state blockgroup faces into a single national index.
    source[0]: states.json
    source[1]: TIGER.zip
    """
    states = json.load(open(source[0].path))
    # Load and index blockgroup shapes
    index = BlockGroupIndex(target[0].path)
    for state in states.values():
        index.add_shapefile(f"{source[1].path}/TIGER/BG/tl_2020_{state['fips']}_bg")
    index.close()


def Point(target, source, env):
    """
    Locate points in the national blockgroup index.
    source[0]: national-blkgrp.pickle
    source[1]: NAD points
    source[2]: AddressPoint points
    """
    index = BlockGroupIndex(source[0].path)
    with gzip.open(target[0].path, "wt", encoding="ascii") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        for s in source[1:]:
            with gzip.open(s.path, "rt", encoding="ascii") as f_in:
                for row in csv.DictReader(f_in):
                    BlockGroup = index.locate(row["X"], row["Y"])
                    if BlockGroup:
                        writer.writerow((row["StreetNum"], row["StreetName"], row["Zip"], BlockGroup))


def Line(target, source, env):
    """
    Extract blockgroups associated with road segments from a TIGER
    FACES/ADDRFEAT file pair, using a list of all counties from the
    frst source file.
    source[0]: counties.txt
    source[1]: TIGER.zip
    """
    files, writers = open_files(target, header)
    counties = [x.strip() for x in open(source[0].path)]
    
    for county in counties:

        # Create index of blockgroups from faces
        faces = shapefile.Reader(f"{source[1].path}/TIGER/FACES/tl_2020_{county}_faces")
        blkgrps = {}
        for i in range(len(faces)):
            record = faces.record(i)
            blkgrps[record["TFID"]] = "".join((
                record["STATEFP"],
                record["COUNTYFP"],
                record["TRACTCE"],
                record["BLKGRPCE"]
            ))
        
        # Write out blockgroups for each street segment
        addrfeat = shapefile.Reader(f"{source[1].path}/TIGER/ADDRFEAT/tl_2020_{county}_addrfeat")
        for i in range(len(addrfeat)):
            record = addrfeat.record(i)
            # Normalize and save record
            StreetName = normalize_street(record["FULLNAME"])
            if StreetName:
                # Left
                ZipCode = record["ZIPL"]
                BlockGroup = blkgrps.get(record["TFIDL"])
                zip2 = ZipCode[:2]
                if zip2 in writers and BlockGroup:
                    writers[zip2].writerow((record["LFROMHN"], StreetName, ZipCode, BlockGroup))
                    writers[zip2].writerow((record["LTOHN"], StreetName, ZipCode, BlockGroup))
                # Right
                ZipCode = record["ZIPR"]
                zip2 = ZipCode[:2]
                BlockGroup = blkgrps.get(record["TFIDR"])
                zip2 = ZipCode[:2]
                if zip2 in writers and BlockGroup:
                    writers[zip2].writerow((record["RFROMHN"], StreetName, ZipCode, BlockGroup))
                    writers[zip2].writerow((record["RTOHN"], StreetName, ZipCode, BlockGroup))

    close_files(files)


def Package(target, source, env):
    """
    Sort and compress StreetNum ranges in Zip/StreetName groups from
    source lookup files.
    """
    package = {}
    lookup = pd.concat(
        [pd.read_csv(s.path, dtype=str) for s in source],
        ignore_index=True
    )
    # Correct zip code formatting
    lookup["Zip"] = lookup["Zip"].str.zfill(5)
    # Keep distinct records
    lookup = lookup.drop_duplicates()
    # StreetNum to int, for sorting
    lookup["StreetNum"] = lookup["StreetNum"].fillna("").str.extract(r"^([1-9][0-9]*)", expand=False)
    lookup = lookup[lookup["StreetNum"].notnull() & (lookup["StreetNum"].str.len() < 7)] # Remove abnormally large street numbers
    lookup["StreetNum"] = lookup["StreetNum"].astype(int)
    # Sort
    lookup = lookup.sort_values(["Zip", "StreetName", "StreetNum", "BlockGroup"])
    # Group by zip/street
    for zip5, streets in groupby(lookup.itertuples(), key=attrgetter("Zip")):
        zip3 = zip5[2:]
        package[zip3] = {}
        for street, nums in groupby(streets, key=attrgetter("StreetName")):
                package[zip3][street] = ([], [])
                for i, num in enumerate(nums):
                    # TODO: resolve same num with multiple blockgroups
                    if i == 0 or num.BlockGroup != package[zip3][street][1][-1]:
                        package[zip3][street][0].append(num.StreetNum)
                        package[zip3][street][1].append(num.BlockGroup)
    with open(target[0].path, "wb") as f:
        pickle.dump(package, f)
