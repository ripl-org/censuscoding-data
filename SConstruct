import json
import os
import pandas as pd
import source.points
import source.lookups

env = Environment(ENV=os.environ)

DOI = "10.5281/zenodo.7382661" # DOI of the replication files at Zenodo

# Load zip code parameters

zip3s = pd.read_csv("data/zip3.csv", dtype=str)
zip2s = sorted(zip3s.zip3.str[:2].unique().tolist())

# Get input files from Zenodo
# NOTE: this will download 20GB of data into the input/ subdirectory!

env.Command(
    target=[
        "input/AddressPoints.zip",
        "input/LICENSE.md",
        "input/NAD_r10.txt.gz",
        "input/NAD_r10.txt.xml",
        "input/SOURCES.md",
        "input/TIGER.zip",
        "input/Validation.zip"
    ],
    source=[
        Value(DOI)
    ],
    action="zenodo_get -o input/ -d $SOURCE"
)

# National index of block groups

env.Command(
  target=[
    "scratch/lookups/national-blkgrp.pickle",
  ],
  source=[
    "data/states.json",
    "input/TIGER.zip"
  ],
  action=source.lookups.NationalBlockGroups
)

# Point-based lookups from National Address Database

env.Command(
  target=[
    f"scratch/points/NAD/{zip2}.csv.gz"
    for zip2 in zip2s
  ],
  source=[
    "input/NAD_r10.txt.gz"
  ],
  action=source.points.NationalAddressDatabase
)

# Point-based lookups from state/local governments

env.Command(
  target=[
    f"scratch/points/AddressPoints/{zip2}.csv.gz"
    for zip2 in zip2s
  ],
  source=[
    "data/AddressPoints.json",
    "input/AddressPoints.zip"
  ],
  action=source.points.AddressPoints
)

for zip2 in zip2s:
  env.Command(
    target=[
      f"scratch/lookups/point/{zip2}.csv.gz"
    ],
    source=[
      f"scratch/lookups/national-blkgrp.pickle",
      f"scratch/points/NAD/{zip2}.csv.gz",
      f"scratch/points/AddressPoints/{zip2}.csv.gz"
    ],
    action=source.lookups.Point
  )

# Line-based lookups from TIGER

env.Command(
  target=[
    f"scratch/lookups/line/{zip2}.csv.gz"
    for zip2 in zip2s
  ],
  source=[
    "data/counties.txt",
    "input/TIGER.zip"
  ],
  action=source.lookups.Line
)

# Package lookups

## point

for zip2 in zip2s:
  env.Command(
    target=[
      f"scratch/package/point/{zip2}"
    ],
    source=[
      f"scratch/lookups/point/{zip2}.csv.gz"
    ],
    action=source.lookups.Package
  )

## line

for zip2 in zip2s:
  env.Command(
    target=[
      f"scratch/package/line/{zip2}"
    ],
    source=[
      f"scratch/lookups/line/{zip2}.csv.gz"
    ],
    action=source.lookups.Package
  )

## all

for zip2 in zip2s:
  env.Command(
    target=[
      f"scratch/package/all/{zip2}"
    ],
    source=[
      f"scratch/lookups/point/{zip2}.csv.gz",
      f"scratch/lookups/line/{zip2}.csv.gz"
    ],
    action=source.lookups.Package
  )

# Validation

## Extract addresses

# env.Command(
#   target=[
#     "scratch/analysis/cms-npi.csv"
#   ],
#   source=[
#     "source/extract-cms-npi.py",
#     "input/Validation/CMS-NPI/20211214/npidata_pfile_20050523-20211212.csv.gz",
#     os.path.join(
#       sharepoint,
#       "Data/Public/CMS-NPI/20211214/pl_pfile_20050523-20211212.csv.gz"
#     )
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# env.Command(
#   target=[
#     "scratch/analysis/epa-frs.csv"
#   ],
#   source=[
#     "source/extract-epa-frs.py",
#     os.path.join(
#       sharepoint,
#       "Data/Public/EPA/Facility Registry System/20220711/NATIONAL_SINGLE.CSV.gz"
#     ),
#     "scratch/lookups/national-blkgrp.dat"
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# env.Command(
#   target=[
#     "scratch/analysis/hud-phb.csv"
#   ],
#   source=[
#     "source/extract-hud-phb.py",
#     os.path.join(
#       sharepoint,
#       "Data/Public/HUD/Public Housing Buildings/20220711/Public_Housing_Buildings.csv"
#     ),
#     "scratch/lookups/national-blkgrp.dat"
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# env.Command(
#   target=[
#     "scratch/analysis/uspto-pat.csv"
#   ],
#   source=[
#     "source/extract-uspto-pat.py",
#     "input/Validation/USPTO/Patent Assignment Dataset/2020/assignment.csv.gz",
#     os.path.join(
#       sharepoint,
#       "Data/Public/USPTO/Patent Assignment Dataset/2020/assignee.csv.gz"
#     )
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# env.Command(
#   target=[
#     "scratch/analysis/uspto-tm.csv"
#   ],
#   source=[
#     "source/extract-uspto-tm.py",
#     os.path.join(
#       sharepoint,
#       "Data/Public/USPTO/Trademark Assignment Dataset/2020/tm_assignment.csv.gz"
#     ),
#     os.path.join(
#       sharepoint,
#       "Data/Public/USPTO/Trademark Assignment Dataset/2020/tm_assignee.csv.gz"
#     )
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# # Censuscode test data with line, point, and all lookups

# tests = {
#   "cms-npi": "year",
#   "epa-frs": "year blkgrp_true",
#   "hud-phb": "year blkgrp_true",
#   "uspto-pat": "year",
#   "uspto-tm": "year"
# }

# for test in tests:
#   for lookup in ["line", "point", "all"]:
#     cols = tests[test]
#     env.Command(
#       target=[
#         f"scratch/analysis/censuscoded/{lookup}/{test}.csv"
#       ],
#       source=[
#         f"scratch/analysis/{test}.csv",
#         f"scratch/package/{lookup}/package.log"
#       ],
#       action=f"python -m censuscoding --data scratch/package/{lookup}/package --preserve-rows --preserve-cols {cols} -i $SOURCE -o $TARGET >${{TARGET}}.log"
#     )

# ### Coverage validation ###

# env.Command(
#   target=[
#     f"scratch/analysis/coverage.csv"
#   ],
#   source=[
#     "source/coverage.py",
#     "data/zip3.csv"
#   ] + [
#     f"scratch/analysis/censuscoded/{lookup}/{test}.csv"
#     for lookup in ["line", "point", "all"]
#     for test in tests
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# env.Command(
#   target=[
#     f"scratch/analysis/coverage.pdf"
#   ],
#   source=[
#     "source/coverage-plot.R",
#     "scratch/analysis/coverage.csv"
#   ],
#   action="Rscript $SOURCES $TARGET >${TARGET}.log"
# )

# ### Accuracy validation ###

# env.Command(
#   target=[
#     f"scratch/analysis/accuracy.csv"
#   ],
#   source=[
#     "source/accuracy.py"
#   ] + [
#     f"scratch/analysis/censuscoded/{lookup}/{test}.csv"
#     for lookup in ["line", "point", "all"]
#     for test in ["epa-frs", "hud-phb"]
#   ],
#   action="python $SOURCES $TARGET >${TARGET}.log"
# )

# env.Command(
#   target=[
#     f"scratch/analysis/accuracy.pdf"
#   ],
#   source=[
#     "source/accuracy-plot.R",
#     "scratch/analysis/accuracy.csv"
#   ],
#   action="Rscript $SOURCES $TARGET >${TARGET}.log"
# )

# # vim: syntax=python expandtab sw=2 ts=2