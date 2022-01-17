import pandas as pd
import sys

in_files = sys.argv[1:-1]
out_file = sys.argv[-1]

lookup = pd.concat([pd.read_csv(f, dtype=str) for f in in_files], ignore_index=True)
lookup.sort_values(["zip", "street"]).drop_duplicates().to_csv(out_file, index=False)
