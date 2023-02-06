import json
import os
import pandas as pd
import source.points
import source.lookups
import source.validation

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

tests = {
  "cms-npi": "year",
  "epa-frs": "year blkgrp_true",
  "hud-phb": "year blkgrp_true",
  "uspto-pat": "year",
  "uspto-tm": "year"
}

## Extract and censuscode test data with line, point, and all lookups

for test in tests:
  env.Command(
    target=[
      f"scratch/validation/extracted/{test}.csv"
    ],
    source=[
      Value(test),
      "input/Validation.zip",
      "scratch/lookups/national-blkgrp.pickle"
    ],
    action=source.validation.Extract
  )
  for lookup in ["line", "point", "all"]:
    cols = tests[test]
    env.Command(
      target=[
        f"scratch/validation/censuscoded/{lookup}/{test}.csv"
      ],
      source=[
        f"scratch/validation/extracted/{test}.csv"
      ]+[
        f"scratch/package/{lookup}/{zip2}"
        for zip2 in zip2s
      ],
      action=f"python -m censuscoding --data scratch/package/{lookup} --preserve-rows --preserve-cols {cols} -i $SOURCE -o $TARGET >${{TARGET}}.log"
    )

## Coverage

env.Command(
  target=[
    f"scratch/validation/coverage.csv"
  ],
  source=[
    "data/zip3.csv"
  ] + [
    f"scratch/validation/censuscoded/{lookup}/{test}.csv"
    for lookup in ["line", "point", "all"]
    for test in tests
  ],
  action=source.validation.Coverage
)

## Accuracy

env.Command(
  target=[
    f"scratch/validation/accuracy.csv"
  ],
  source=[
    f"scratch/validation/censuscoded/{lookup}/{test}.csv"
    for lookup in ["line", "point", "all"]
    for test in ["epa-frs", "hud-phb"]
  ],
  action=source.validation.Accuracy
)

## Plots

env.Command(
  target=[
    f"scratch/validation/coverage.pdf"
  ],
  source=[
    "source/plots/coverage.R",
    "scratch/validation/coverage.csv"
  ],
  action="Rscript $SOURCES $TARGET >${TARGET}.log"
)
env.Command(
  target=[
    f"scratch/validation/accuracy.pdf"
  ],
  source=[
    "source/plots/accuracy.R",
    "scratch/validation/accuracy.csv"
  ],
  action="Rscript $SOURCES $TARGET >${TARGET}.log"
)

# vim: syntax=python expandtab sw=2 ts=2