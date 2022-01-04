import address
import csv
import gzip
import sys

in_file, out_file = sys.argv[1:]

with gzip.open(in_file, "rt", encoding="utf-8") as fin:
    reader = csv.DictReader(fin)
    with gzip.open(out_file, "wt") as fout:
        writer = csv.writer(fout)
        writer.writerow(("X", "Y", "StreetNum", "StreetName", "Zip"))
        for record in reader:
            # Normalize and save record
            StreetName = address.normalize(f"{record['Add_Number']} {record['StN_PreDir']} {record['StreetName']}")
            if StreetName is not None:
                writer.writerow((record["Longitude"], record["Latitude"], record["Add_Number"], StreetName, record["Zip_Code"]))
