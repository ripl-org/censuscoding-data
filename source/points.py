import csv
import gzip
import io
import json
import os
import re
from zipfile import ZipFile

from source.address import extract_street_num, normalize_street, transliterate
from source.utils import open_files, close_files

header = ["X", "Y", "StreetNum", "StreetName", "Zip"]
re_point = re.compile(r"^POINT \(([\-\.\d]+) ([\-\.\d]+)\)$")


def _normalize_zip(z):
    """
    Pad with zeroes to either 5 or 9 digit zip code, then truncate
    to 5 digits.
    """
    if len(z) > 5:
        z = z.zfill(9)
    else:
        z = z.zfill(5)
    return z[:5]


def _read_csv(fileobj, config):
    """
    Read a CSV file using the field mapping in config.
    Yield one line at a time with normalized X, Y, StreetNum, StreetName, Zip.
    """
    for line in csv.DictReader(fileobj):
        if "Point" in config:
            p = re_point.match(line[config["Point"]])
            try:
                X = p.group(1)
                Y = p.group(2)
            except:
                X = ""
                Y = ""
        else:
            X = line[config.get("X", "X")]
            Y = line[config.get("Y", "Y")]
        if "Address" in config:
            StreetNum = extract_street_num(line[config["Address"]].strip())
            StreetName = normalize_street(line[config["Address"]].strip())
        else:
            StreetNum = line[config["StreetNum"]].strip()
            if "StreetDir" in config:
                StreetName = "{} {}".format(line[config["StreetDir"]], line[config["StreetName"]].lstrip("0")).strip()
            else:
                StreetName = line[config["StreetName"]].lstrip("0")
        Zip = _normalize_zip(line[config["Zip"]][:5])
        yield (X, Y, StreetNum, transliterate(StreetName).strip(), Zip)


def _read_geojson(fileobj):
    """
    Read a GeoJSON file from OpenAddresses.
    Yield one line at a time with normalized X, Y, StreetNum, StreetName, Zip.
    """
    for i, line in enumerate(fileobj, start=1):
        # Load json record
        try:
            record = json.loads(line)
        except e:
            print(f"warning: improper JSON format at line {i}:", str(e))
            continue
        try:
            X = str(record["geometry"]["coordinates"][0])
            Y = str(record["geometry"]["coordinates"][1])
            StreetNum = record["properties"]["number"]
            StreetName = record["properties"]["street"]
            Zip = _normalize_zip(record["properties"]["postcode"])
            yield (X, Y, StreetNum, transliterate(StreetName), Zip)
        except:
            print("warning: unexpected GeoJSON format at line", i)
            continue


def NationalAddressDatabase(target, source, env):
    """
    Extract address points from National Address Database.
    Save to gzipped CSV files organization by leading 2-digits
    of zip code (zip2).
    """
    files, writers = open_files(target, header)
    with gzip.open(source[0].path, "rt", encoding="utf-8") as f:
        idx = [0,7,12,15,20,30,31]
        reader = csv.reader(f)
        next(reader) # Remove header
        for line in reader:
            if len(line) <= 31:
                print("ERROR in line:", line)
            else:
                Zip = line[7]
                zip2 = Zip[:2]
                if zip2 in writers:
                    X = line[30]
                    Y = line[31]
                    StreetNum = line[20]
                    StreetName = "{} {}".format(line[12], line[15]).strip()
                    writers[zip2].writerow((X, Y, StreetNum, transliterate(StreetName), Zip))
    close_files(files)


def AddressPoints(target, source, env):
    """
    Extract address points from a CSV or GeoJSON state/local address
    source, with configurations specified by the first source file.
    Save to gzipped CSV files organization by leading 2-digits
    of zip code (zip2).
    source[0]: AddressPoints.json
    source[1]: AddressPoints.zip
    """
    files, writers = open_files(target, header)
    datasets = json.load(open(source[0].path))
    with ZipFile(source[1].path) as z:
        for dataset in datasets:
            filename = "/".join(("AddressPoints", dataset["name"], dataset["date"], dataset["filename"]))
            with z.open(filename) as f:
                with gzip.GzipFile(fileobj=f, mode="rb") as g:
                    print(filename)
                    if filename.endswith(".csv.gz"):
                        reader = _read_csv(io.TextIOWrapper(g, encoding=dataset.get("encoding", "utf-8")), dataset["config"])
                    elif filename.endswith(".geojson.gz"):
                        reader = _read_geojson(io.TextIOWrapper(g, encoding=dataset.get("encoding", "utf-8")))
                    else:
                        raise ValueError(f"unknown file type for {filename}")
                    for record in reader:
                        zip2 = record[-1][:2]
                        if zip2 in writers:
                            writers[zip2].writerow(record)
    close_files(files)
