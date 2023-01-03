import csv
import gzip
import json
import os
import pickle
import rtree
import shapefile
import sys
import tempfile
from itertools import groupby
from operator import attrgetter
from shapely.geometry import shape
from zipfile import ZipFile

from source.address import normalize_street
from source.utils import re_num, open_files, close_files


shapefile_exts = [".cpg", ".dbf", ".prj", ".shp", ".shp.ea.iso.xml", ".shp.iso.xml", ".shx"]
header = ["StreetNum", "StreetName", "Zip", "BlockGroup"]


def _locate(shape_index, x, y):
    """
    Use the prebuilt shape `index` to locate a blockgroup ID.
    """
    p = Point(float(x), float(y))
    for match in shape_index.intersection(p.bounds, "raw"):
        if p.intersects(match["shape"]):
            return match["geoid"]


def NationalBlockGroups(target, source, env):
    """
    Combine all state blockgroup faces into a single national index.
    source[0]: states.json
    source[1]: TIGER.zip
    """
    out_prefix = target[0].rpartition(".")[0]
    states = json.load(open(source[0]))
    # Load and index blockgroup shapes
    shape_index = rtree.index.Index(out_prefix)
    with ZipFile(source[1]) as tiger_zip:
        n = 0
        for state in states.values():
            # Extract state blockgroup shapefile to temp dir
            temp_dir = tempfile.TemporaryDirectory()
            filename = f"TIGER/BLKGRP/tl_2020_{state['fips']}_bg"
            for ext in shapefile_exts:
                tiger_zip.extract(f"{filename}{ext}", path=temp_dir.name)
            blkgrp = shapefile.Reader(os.path.join(temp_dir.name, filename))
            for i in range(len(blkgrp)):
                s = shape(blkgrp.shape(i))
                shape_index.insert(
                    n,
                    s.bounds,
                    {
                        "geoid": blkgrp.record(i)["GEOID"],
                        "shape": s
                    }
                )
                n += 1
            temp_dir.cleanup()
    shape_index.close()


def Point(target, source, env):
    """
    Locate points in the national blockgroup index.
    source[0]: national-blkgrp.dat
    source[1]: NAD points
    source[2]: AddressPoint points
    """
    shape_index = rtree.index.Index(source[0].rpartition(".")[0])
    with gzip.open(target[0], "wt", encoding="ascii") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        for filename in source[1:]:
            with gzip.open(filename, "rt", encoding="ascii") as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    BlockGroup = _locate(shape_index, row["X"], row["Y"])
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
    counties = [x.strip() for x in open(source[0])]
    with ZipFile(source[1]) as tiger_zip:
        for county in counties:
            with tempfile.TemporaryDirectory() as temp_dir:

                # Extract county faces shepefile to temp dir
                filename = f"TIGER/FACES/tl_2020_{county}_faces"
                for ext in shapefile_exts:
                    tiger_zip.extract(f"{filename}{ext}", path=temp_dir.name)
                faces = shapefile.Reader(os.path.join(temp_dir.name, filename))

                # Create index of blockgroups from faces
                blkgrps = {}
                for i in range(len(faces)):
                    record = faces.record(i)
                    blkgrps[record["TFID"]] = "".join((
                        record["STATEFP"],
                        record["COUNTYFP"],
                        record["TRACTCE"],
                        record["BLKGRPCE"]
                    ))

                # Extract county addrfeat shapefile to temp dir
                filename = f"TIGER/ADDRFEAT/tl_2020_{county}_addrfeat"
                for ext in shapefile_exts:
                    tiger_zip.extract(f"{filename}{ext}", path=temp_dir.name)
                addrfeat = shapefile.Reader(os.path.join(temp_dir.name, filename))

                # Write out blockgroups for each street segment
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
                            StreetNum = re_num.match(record["LFROMHN"])
                            if StreetNum:
                                writers[zip2].writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                            StreetNum = re_num.match(record["LTOHN"])
                            if StreetNum:
                                writers[zip2].writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                        # Right
                        ZipCode = record["ZIPR"]
                        zip2 = ZipCode[:2]
                        BlockGroup = blkgrps.get(record["TFIDR"])
                        zip2 = ZipCode[:2]
                        if zip2 in writers and BlockGroup:
                            StreetNum = re_num.match(record["RFROMHN"])
                            if StreetNum:
                                writers[zip2].writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                            StreetNum = re_num.match(record["RTOHN"])
                            if StreetNum:
                                writers[zip2].writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
    close_files(files)


def Package(target, source, env):
    """
    Sort and compress StreetNum ranges in Zip/StreetName groups from
    source lookup files.
    """
    package = {}
    lookup = pd.concat(
        [pd.read_csv(filename, dtype=str) for filename in source],
        ignore_index=True
    )
    # Correct zip code formatting
    lookup["Zip"] = lookup["Zip"].str.zfill(5)
    # Keep distinct records
    lookup = lookup.drop_duplicates()
    # StreetNum to int, for sorting
    lookup["StreetNum"] = lookup["StreetNum"].astype(int)
    # Sort
    lookup = lookup.sort_values(["Zip", "StreetName", "StreetNum", "BlockGroup"])
    # Group by zip/street
    for zip5, streets in groupby(lookup.itertuples, key=attrgetter("Zip")):
        zip3 = zip5[2:]
        package[zip3] = {}
        for street, nums in groupby(streets, key=attrgetter("StreetName")):
                package[zip3][street] = ([], [])
                for i, num in enumerate(nums):
                    # TODO: resolve same num with multiple blockgroups
                    if i == 0 or num.BlockGroup != package[zip3][street][1][-1]:
                        package[zip3][street][0].append(num.StreetNum)
                        package[zip3][street][1].append(num.BlockGroup)
    with open(target[0], "wb") as f:
        pickle.dump(package, f)
