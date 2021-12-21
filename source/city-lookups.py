import pandas as pd
import sys

blocks_file, geo_level, name_file, num_file = sys.argv[1:]

blocks = pd.read_csv(blocks_file, dtype=str)

index = ["StreetName", "City"]

names = blocks.drop_duplicates(index + [geo_level]).groupby(index).filter(lambda x: len(x)==1)
names = names.loc[names[geo_level].notnull(), index + [geo_level]]
names.to_csv(name_file, index=False)
print(len(names), "street names with unique", geo_level)

done = names[index]
done["done"] = True

blocks = blocks.merge(done, how="left", on=index)
blocks = blocks[blocks.done.isnull()]

index = ["StreetNum", "StreetName", "City"]

nums = blocks.drop_duplicates(index + [geo_level]).groupby(index).filter(lambda x: len(x)==1)
nums = nums.loc[nums[geo_level].notnull(), index + [geo_level]]
nums.to_csv(num_file, index=False)
print(len(nums), "street nums/names with unique", geo_level)

