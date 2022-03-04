import csv
import gzip
import re
import sys
from source.address import normalize_directional, transliterate

in_file, out_file = sys.argv[1:]

re_num = re.compile(r"^([1-9][0-9]*)")

with gzip.open(in_file, "rt", encoding="latin1") as fin:
    reader = csv.DictReader(fin)
    with gzip.open(out_file, "wt", encoding="ascii") as fout:
        writer = csv.writer(fout)
        writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
        for record in reader:
            # Normalize and save record
            StreetNum = re_num.match(record["Add_Number"])
            StreetName = transliterate(record["StreetName"])
            if record["StN_PreDir"]:
                directional = normalize_directional(record["StN_PreDir"])
                if directional:
                    StreetName = f"{directional} {StreetName}"
            if StreetNum is not None and StreetName:
                writer.writerow((record["Longitude"], record["Latitude"], StreetNum.group(1), StreetName, record["Zip_Code"]))
