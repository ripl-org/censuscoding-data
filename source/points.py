import csv
import gzip
import os
import re
from zipfile import ZipFile

from source.address import extract_street_num, normalize_street, transliterate


re_num   = re.compile(r"^([1-9][0-9]*)")
re_point = re.compile(r"^POINT \(([\-\.\d]+) ([\-\.\d]+)\)$")


def _open_files(filenames):
    files = {}
    writers = {}
    for filename in filenames:
        zip2 = os.path.basename(filename).partition(".")[0]
        files[zip2] = gzip.open(filename, "wt", encoding="ascii")
        writers[zip2] = csv.writer(filename[zip2])
        writers[zip2].writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
    return files, writers


def _close_files(files):
    for f in files.values():
        f.close()


def _read_csv(fileobj, config):
    """
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
            StreetNum = extract_street_num(line[config["Address"]])
            StreetName = normalize_street(line[config["Address"]])
        else:
            StreetNum = re_num.match(line[config["StreetNum"]])
            if StreetNum is not None:
                StreetNum = StreetNum.group(1)
            else:
                StreetNum = ""
            if "StreetDir" in config:
                StreetName = "{} {}".format((line[config["StreetDir"]], line[config["StreetName"]].lstrip("0"))).strip()
            else:
                StreetName = line[config["StreetName"]].lstrip("0")
        Zip = line[config["Zip"]][:5]
        yield (X, Y, StreetNum, transliterate(StreetName), Zip)


def _read_geojson(fileobj):
    """
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
            Zip = record["properties"]["postcode"]
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
    files, writers = _open_files(target)
    with gzip.open(source[0], "rt", encoding="utf-8") as f:
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
                    StreetName = "{} {}".format((line[12], line[15])).strip()
                    writers[zip2].writerow((X, Y, StreetNum, transliterate(StreetName), Zip))
    _close_files(files)


def AddressPoints(target, source, env):
    """
    """
    files, writers = _open_files(target)
    with open(source[0]) as f:
        datasets = json.read(f)
    with ZipFile(source[1]) as z:
        for dataset in datasets:
            filename = "/".join((dataset["name"], dataset["date"], dataset["filename"]))
            with z.open(filename) as f:
                with gzip.GZipFile(fileobj=f) as g:
                    if filename.endswith(".csv.gz"):
                        reader = _read_csv(g, dataset["config"])
                    elif filename.endswith(".geojson.gz"):
                        reader = _read_geojson(g)
                    else:
                        pass
                    for record in reader:
                        zip2 = record[-1][:2]
                        if zip2 in writers:
                            writers[zip2].writerrow(record)
    _close_files(files)