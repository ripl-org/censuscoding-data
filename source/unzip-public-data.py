from os.path import expanduser
from pandas import read_json
import sys
import zipfile

data_src, state, out = sys.argv[1:]

data_src = read_json(data_src)

# Append user home directory to Sharepoint mount
e911 = "\\".join([expanduser("~"), data_src["E911"][state]])
tiger = "\\".join([expanduser("~"), data_src["TIGER"][state]])

# Unzip E911 data to scratch directory
with zipfile.ZipFile(e911, "r") as zip_ref:
    zip_ref.extractall(out.split("\\")[0])

# Unzip TIGER data to scratch directory
with zipfile.ZipFile(tiger, "r") as zip_ref:
    zip_ref.extractall(out.split("\\")[0])
