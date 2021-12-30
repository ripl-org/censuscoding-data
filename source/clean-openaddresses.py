import gzip
import json
import pandas as pd
import sys
import usaddress

geojson_file, out_file = sys.argv[1:]

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

    # Tag address with usaddress
    try:
        address = f"{StreetNum} {StreetName}"
        tags = usaddress.tag(address)
    except:
        print("error: cannot tag address", address)
        continue

    # Interpret tags to determine StreetNum and StreetName
    if len(tags) < 1:
        print("warning: empty tags for address", address)
        continue
    tags = tags[0]
    if "AddressNumber" in tags and ("StreetName" in tags or "StreetNamePreDirectional" in tags): 
        StreetNum = tags["AddressNumber"]
        if "StreetNamePreDirectional" in tags and "StreetName" in tags:
            StreetName = f"{tags['StreetNamePreDirectional']} {tags['StreetName']}"
        elif "StreetNamePreDirectional" in tags:
            StreetName = tags["StreetNamePreDirectional"]
        else:
            StreetName = tags["StreetName"]
    else:
        print("warning: missing streetnum or streetname for address", address)
        continue

    # Save record
    data["X"].append(X)
    data["Y"].append(Y)
    data["StreetNum"].append(StreetNum)
    data["StreetName"].append(StreetName)
    data["Zip"].append(Zip)


# Print output to CSV
df = pd.DataFrame(data)
df.to_csv(out_file, index=False)
