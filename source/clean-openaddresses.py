import gzip
import json
import pandas as pd
import sys

geojson_file, out_file = sys.argv[1:]

data = {
	"num": [],
	"street": [],
	"zipcode": [],
	"lat": [],
	"lon": []
}

for i, line in enumerate(gzip.open(geojson_file), start=1):
    try:
        record = json.loads(line)
    except e:
        print(f"warning: improper JSON format at line {line}:", str(e))
        continue
    try:
    	num = record["properties"]["number"].partition("-")[0]
    	street = record["properties"]["street"]
    	zipcode = record["properties"]["postcode"]
    	lat = str(record["geometry"]["coordinates"][1])
    	lon = str(record["geometry"]["coordinates"][0])
    except:
    	print("warning: unexpected GeoJSON format at line", line)
    	continue
    data["num"].append(num)
    data["street"].append(street)
    data["zipcode"].append(zipcode)
    data["lat"].append(lat)
    data["lon"].append(lon)

df = pd.DataFrame(data)
df.to_csv(out_file, index=False)
