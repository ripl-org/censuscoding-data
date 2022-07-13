import csv
import gzip
import os
import re
import shapefile
import sys
import zipfile
from address import normalize_street

addrfeat_file, faces_file, out_file = sys.argv[1:]

re_num = re.compile(r"^([1-9][0-9]*)")

out_dir = os.path.dirname(out_file)

with zipfile.ZipFile(addrfeat_file) as z:
    z.extractall(out_dir)

with zipfile.ZipFile(faces_file) as z:
    z.extractall(out_dir)

blkgrps = {}
faces = shapefile.Reader(os.path.join(out_dir, os.path.basename(faces_file)[:-4]))
for i in range(len(faces)):
    record = faces.record(i)
    blkgrps[record["TFID"]] = "".join((
        record["STATEFP"],
        record["COUNTYFP"],
        record["TRACTCE"],
        record["BLKGRPCE"]
    ))

addrfeat = shapefile.Reader(os.path.join(out_dir, os.path.basename(addrfeat_file)[:-4]))
with gzip.open(out_file, "wt", encoding="ascii") as fout:
    writer = csv.writer(fout)
    writer.writerow(("StreetNum", "StreetName", "Zip", "BlockGroup"))
    n = 0
    for i in range(len(addrfeat)):
        record = addrfeat.record(i)
        # Normalize and save record
        StreetName = normalize_street(record["FULLNAME"])
        if StreetName:
            # Left
            ZipCode = record["ZIPL"]
            BlockGroup = blkgrps.get(record["TFIDL"])
            if ZipCode and BlockGroup:
                StreetNum = re_num.match(record["LFROMHN"])
                if StreetNum:
                    writer.writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                    n += 1
                StreetNum = re_num.match(record["LTOHN"])
                if StreetNum:
                    writer.writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                    n += 1
            # Right
            ZipCode = record["ZIPR"]
            BlockGroup = blkgrps.get(record["TFIDR"])
            if ZipCode and BlockGroup:
                StreetNum = re_num.match(record["RFROMHN"])
                if StreetNum:
                    writer.writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                    n += 1
                StreetNum = re_num.match(record["RTOHN"])
                if StreetNum:
                    writer.writerow((StreetNum.group(1), StreetName, ZipCode, BlockGroup))
                    n += 1

print(i, "records")
print(n, "addresses found")
