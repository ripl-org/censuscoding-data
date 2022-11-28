import pandas as pd
import sys

blocks_file, geo_level, name_file, num_file = sys.argv[1:]

blocks = pd.read_csv(blocks_file, dtype=str)
n = len(blocks)

blocks.loc[:,"Zip"] = blocks.Zip.str.extract(r"(\d+)", expand=False)
blocks = blocks[blocks.Zip.notnull() & (blocks.Zip.str.len() == 5)]
blocks["Zip"] = blocks.Zip.astype(int)
print("dropped", n - len(blocks), "records with missing or invalid 5-digit zip")

index = ["StreetName", "Zip"]

names = blocks.drop_duplicates(index + [geo_level]).groupby(index).filter(lambda x: len(x)==1)
names = names.loc[names[geo_level].notnull(), index + [geo_level]]
print(len(names), "street names with unique", geo_level)

done = names[index]
done["done"] = True

blocks = blocks.merge(done, how="left", on=index)
blocks = blocks[blocks.done.isnull()]

index = ["StreetNum", "StreetName", "Zip"]

nums = blocks.drop_duplicates(index + [geo_level]).groupby(index).filter(lambda x: len(x)==1)
nums = nums.loc[nums[geo_level].notnull(), index + [geo_level]]

# Rename columns as required by censuscoding pkg
names.rename(columns={"StreetName": "street", "Zip": "zip", "BlockGroup": "blkgrp"}, inplace=True)
nums.rename(columns={"StreetNum": "street_num", "StreetName": "street", "Zip": "zip", "BlockGroup": "blkgrp"}, inplace=True)
names.to_csv(name_file, columns=["zip", "street", "blkgrp"], index=False)
nums.to_csv(num_file, columns=["zip", "street", "street_num", "blkgrp"], index=False)

print(len(nums), "street nums/names with unique", geo_level)

