import gzip
import json
import pandas as pd
import re
import sys
from address import extract_street_num, normalize_street

geojson_file, out_file = sys.argv[1:]

re_num = re.compile(r"[0-9]+")

data = {
    "X": [],
    "Y": [],
    "StreetNum": [],
    "StreetName": [],
    "Zip": [],
}

for i, line in enumerate(gzip.open(geojson_file), start=1):

    # Load json record
    try:
        record = json.loads(line)
    except e:
        print(f"warning: improper JSON format at line {line}:", str(e))
        continue
    try:
        X = str(record["geometry"]["coordinates"][0])
        Y = str(record["geometry"]["coordinates"][1])
        StreetNum = record["properties"]["number"]
        StreetName = record["properties"]["street"]
        Zip = record["properties"]["postcode"]
    except:
        print("warning: unexpected GeoJSON format at line", line)
        continue

    # Normalize and save record
    StreetNum = extract_street_num(StreetNum).strip("*")
    StreetName = normalize_street(f"{StreetNum} {StreetName}")
    if re_num.fullmatch(StreetNum) is not None and StreetName is not None:
        data["X"].append(X)
        data["Y"].append(Y)
        data["StreetNum"].append(StreetNum)
        data["StreetName"].append(StreetName)
        data["Zip"].append(Zip)

# Print output to CSV
df = pd.DataFrame(data)
df.to_csv(out_file, encoding="ascii", index=False)
