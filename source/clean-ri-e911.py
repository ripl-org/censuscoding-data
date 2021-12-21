import pandas as pd
import numpy as np
import re
import sys
import usaddress

def upper(x):
    return "".join(c for c in x.upper() if c.isalpha() or c==" ")

def upper_alphanum(x):
    return "".join(c for c in x.upper() if c.isalnum() or c==" ")

sites_file, out_file = sys.argv[1:]

### NOTE: As of 2021/12/07 E911 sites .csv column names have changes    ###
###   - The code below renames to old colnames in order to change as little
###     down-stream code as possible.
old_columns = ["ESiteID", "X", "Y", "Zip", "ZN", "HouseNumbe", "PrimaryNam", "Alias1", "Alias2", "Alias3", "Alias4", "Alias5"]
new_columns = ["OBJECTID", "X", "Y", "Post_Code", "MSAGComm", "AddNumFull", "St_Full", "St_Alias1", "St_Alias2", "St_Alias3", "St_Alias4", "St_Alias5"]

sites = pd.read_csv(sites_file, usecols=new_columns, low_memory=False)
sites.rename(columns=dict(zip(new_columns, old_columns)), inplace=True)
sites[["ALIName"]] = sites[["PrimaryNam"]]

# Retain sites with known lat/lon
sites = sites[sites.X.notnull() & sites.Y.notnull()]

sites["City"] = sites.ZN.str.partition(" / ")[0]

sites["ALIName"] = np.where(sites["PrimaryNam"]==sites["ALIName"], "", sites["ALIName"])
sites["ALIName"].replace("", np.nan, inplace=True)

for col in ["Alias1", "Alias2", "Alias3", "Alias4", "Alias5"]:
    sites[col].replace(" ", np.nan, inplace=True)

sites = pd.melt(sites,
                id_vars=["ESiteID", "X", "Y", "City", "Zip", "HouseNumbe"], 
                value_vars=["PrimaryNam", "ALIName", "Alias1", "Alias2", "Alias3", "Alias4", "Alias5"])

sites = sites.dropna()
sites = sites[["ESiteID", "X", "Y", "HouseNumbe", "value", "City", "Zip"]]
sites = sites.rename(columns={"value": "Street", "HouseNumbe": "HouseNum"}).reset_index()

# Custom fix because of error in parsing of string
#sites["Street"] = np.where(sites.Street.str.contains("HWY "), sites["Street"].str.replace(" ", ""), sites["Street"])

# Drop all letters from house number field
sites["HouseNum"] = sites.HouseNum.apply(lambda x: re.sub("[^0-9]", "", x.partition("-")[0]))

# Concat house number and street fields as this yields better results than street alone
sites["FullStreet"] = sites.HouseNum + " " + sites.Street

# Run usaddress tag on full street field
def tag(x):
    try: 
        return usaddress.tag(x)[0]
    except usaddress.RepeatedLabelError:
        return usaddress.tag("")[0]

tagged = pd.DataFrame(sites.FullStreet.apply(upper_alphanum).apply(tag).tolist())
pd.testing.assert_index_equal(tagged.index, sites.index)

tagged["Directional"] = np.where(tagged.StreetNamePreDirectional.notnull(), tagged.StreetNamePreDirectional, tagged.StreetNamePostDirectional)

sites["StreetNum"] = np.where(tagged.AddressNumber.str.isdigit()==True, tagged.AddressNumber, np.nan)
sites["StreetName"] = np.where(tagged.Directional.notnull(), tagged.Directional + " " + tagged.StreetName, tagged.StreetName)

i = tagged.AddressNumber.str.isdigit() == False
print(i.sum(), "non-numeric street numbers")
sites.loc[i, "StreetName"] = tagged.loc[i, "AddressNumber"] + " " + sites.loc[i, "StreetName"]

sites["StreetName"] = np.where(sites.StreetName.isnull() ,tagged.StreetNamePostDirectional, sites.StreetName)

columns = ["X", "Y", "StreetNum", "StreetName", "City", "Zip"]

sites[columns].drop_duplicates(columns).sort_values(["City", "StreetName", "StreetNum"]).to_csv(out_file, index=False)