import gzip
import json
import pandas as pd
import sys

geojson_file, out_file = sys.argv[1:]

data = {
    "X": [],
    "Y": [],
    "StreetNum": [],
    "StreetName": [],
    "Zip": [],
}

for i, line in enumerate(gzip.open(geojson_file), start=1):
    try:
        record = json.loads(line)
    except e:
        print(f"warning: improper JSON format at line {line}:", str(e))
        continue
    try:
        X = str(record["geometry"]["coordinates"][0])
        Y = str(record["geometry"]["coordinates"][1])
        StreetNum = record["properties"]["number"].partition("-")[0]
        StreetName = record["properties"]["street"]
        Zip = record["properties"]["postcode"]
    except:
        print("warning: unexpected GeoJSON format at line", line)
        continue
    data["X"].append(X)
    data["Y"].append(Y)
    data["StreetNum"].append(StreetNum)
    data["StreetName"].append(StreetName)
    data["Zip"].append(Zip)

df = pd.DataFrame(data)
df.to_csv(out_file, index=False)
