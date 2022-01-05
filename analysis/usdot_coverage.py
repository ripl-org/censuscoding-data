import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import gzip
import os


directory = "C://Users/MarcelleGoggins/Research Improving People's Lives/RIPL All Staff - Documents/Data/Public/USDOT/National Address Database/20211221/"

zipcodes = set()
address_counts = dict()
counter = 0
with gzip.open(os.path.join(directory,"NAD_r8.txt.gz"), "rt", encoding="utf-8") as fin:
    reader = csv.reader(fin)
    next(reader) # skip header
    for line in reader:
        zip = line[7]
        zipcodes.add(zip) 
        if zip not in address_counts.keys():
            address_counts[zip] = 1
        else:
            address_counts[zip] += 1
        counter += 1
        if counter%10000==0:
            print(counter)

# Visualize # of addresses per zip code
df = pd.DataFrame(address_counts.items(),columns=['zip','count'])



df2 = df.head(20)

plt.figure()
sns.histplot(data=df, x="zip", y="count",).set(
    title="Address Counts by Zip Code")
plt.xlabel("Zip Code")
plt.ylabel("Count")
plt.xticks(size=5,rotation=90)
plt.tight_layout()
plt.show()