import pandas as pd
import sys

csvfile = sys.argv[1:]

sites = pd.read_csv(csvfile)

