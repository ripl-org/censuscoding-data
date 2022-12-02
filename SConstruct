import json
import os
import source.lookups

env = Environment(ENV=os.environ)
sharepoint = os.path.join(
  os.path.expanduser("~"),
  "Research Improving People's Lives",
  "RIPL All Staff - Documents"
)
tiger = os.path.join(sharepoint, "Data", "Public", "TIGER", "2020")
counties = [x.strip() for x in open("counties.txt")]
states = json.load(open("states.json"))
state_fips = json.load(open("state-fips.json"))

#env.CacheDir(os.path.join(sharepoint, "Data/Public/Censuscoding/scons-cache"))

# National blkgrp file

env.Command(
  target=[
    "scratch/lookups/national-blkgrp.dat",
    "scratch/lookups/national-blkgrp.idx"
  ],
  source=[
    "source/build-national-blkgrp.py"
  ]+[
    os.path.join(sharepoint, f"Data/Public/TIGER/2020/tl_2020_{config['fips']}_bg.shp")
    for config in state_fips.values()
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

# Line-based lookups from TIGER

for county in counties:

  env.Depends(
    env.Command(
      target=[
        f"scratch/lookups/line/{county}/address-blkgrp.csv.gz",
        f"scratch/lookups/line/{county}/address-blkgrp.log"
      ],
      source=[
        "source/clean-tiger.py",
        os.path.join(tiger, "ADDRFEAT", f"tl_2020_{county}_addrfeat.zip"),
        os.path.join(tiger, "FACES", f"tl_2020_{county}_faces.zip")
      ],
      action="python $SOURCES ${TARGETS[0]} >${TARGETS[1]}"
    ),
    ["source/address.py"]
  )

  env.Command(
    target=[
      f"scratch/lookups/line/{county}/lookup-street.csv.gz",
      f"scratch/lookups/line/{county}/lookup-street-num.csv.gz",
      f"scratch/lookups/line/{county}/lookup-street.log"
    ],
    source=[
      "source/build-lookups.py",
      f"scratch/lookups/line/{county}/address-blkgrp.csv.gz",
      Value("BlockGroup")
    ],
    action="python $SOURCES ${TARGETS[0]} ${TARGETS[1]} >${TARGETS[2]}"
  )

# Point-based lookups from NAD and states/counties/cities

for state, config in states.items():

  env.Depends(
    env.Command(
      target=[
        f"scratch/lookups/point/{state}/address.csv.gz",
        f"scratch/lookups/point/{state}/address.log"
      ],
      source=[
        "source/clean-{}.py".format(config["address"]["method"]),
        os.path.join(sharepoint, config["address"]["path"])
      ],
      action="python $SOURCES ${TARGETS[0]} >${TARGETS[1]}"
    ),
    ["source/address.py"]
  )

  env.Command(
    target=[
      f"scratch/lookups/point/{state}/address-blkgrp.csv.gz",
      f"scratch/lookups/point/{state}/address-blkgrp.log"
    ],
    source=[
      "source/locate-blkgrp.py",
      os.path.join(sharepoint, config["blkgrp"]["path"]),
      f"scratch/lookups/point/{state}/address.csv.gz"
    ],
    action="python $SOURCES ${TARGETS[0]} >${TARGETS[1]}"
  )

  env.Command(
    target=[
      f"scratch/lookups/point/{state}/lookup-street.csv.gz",
      f"scratch/lookups/point/{state}/lookup-street-num.csv.gz",
      f"scratch/lookups/point/{state}/lookup-street.log"
    ],
    source=[
      "source/build-lookups.py",
      f"scratch/lookups/point/{state}/address-blkgrp.csv.gz",
      Value("BlockGroup")
    ],
    action="python $SOURCES ${TARGETS[0]} ${TARGETS[1]} >${TARGETS[2]}"
  )

# Merge and package lookups

## line

env.Command(
  target=[
    "scratch/lookups/line/street.json.gz"
  ],
  source=[
    f"scratch/lookups/line/{county}/lookup-street.csv.gz" for county in counties
  ],
  action=source.lookups.MergeStreet
)

env.Command(
  target=[
    "scratch/lookups/line/street-num.json.gz"
  ],
  source=(
    ["scratch/lookups/line/street.json.gz"] +
    [f"scratch/lookups/line/{county}/lookup-street-num.csv.gz" for county in counties]
  ),
  action=source.lookups.MergeStreetNum
)

env.Command(
  target=[
    "scratch/package/line/package.log"
  ],
  source=[
    "scratch/lookups/line/street-num.json.gz"
  ],
  action=source.lookups.Package
)

## point

env.Command(
  target=[
    "scratch/lookups/point/street.json.gz"
  ],
  source=[
    f"scratch/lookups/point/{state}/lookup-street.csv.gz" for state in states
  ],
  action=source.lookups.MergeStreet
)

env.Command(
  target=[
    "scratch/lookups/point/street-num.json.gz"
  ],
  source=(
    ["scratch/lookups/point/street.json.gz"] +
    [f"scratch/lookups/point/{state}/lookup-street-num.csv.gz" for state in states]
  ),
  action=source.lookups.MergeStreetNum
)

env.Command(
  target=[
    "scratch/package/point/package.log"
  ],
  source=[
    "scratch/lookups/point/street-num.json.gz"
  ],
  action=source.lookups.Package
)

## all

env.Command(
  target=[
    "scratch/lookups/all/street.json.gz"
  ],
  source=(
    [f"scratch/lookups/line/{county}/lookup-street.csv.gz" for county in counties] +
    [f"scratch/lookups/point/{state}/lookup-street.csv.gz" for state in states]
  ),
  action=source.lookups.MergeStreet
)

env.Command(
  target=[
    "scratch/lookups/all/street-num.json.gz"
  ],
  source=(
    ["scratch/lookups/all/street.json.gz"] +
    [f"scratch/lookups/line/{county}/lookup-street-num.csv.gz" for county in counties] +
    [f"scratch/lookups/point/{state}/lookup-street-num.csv.gz" for state in states]
  ),
  action=source.lookups.MergeStreetNum
)

env.Command(
  target=[
    "scratch/package/all/package.log"
  ],
  source=[
    "scratch/lookups/all/street-num.json.gz"
  ],
  action=source.lookups.Package
)

# Analysis data

## Extract addresses

env.Command(
  target=[
    "scratch/analysis/cms-npi.csv"
  ],
  source=[
    "source/extract-cms-npi.py",
    os.path.join(
      sharepoint,
      "Data/Public/CMS-NPI/20211214/npidata_pfile_20050523-20211212.csv.gz"
    ),
    os.path.join(
      sharepoint,
      "Data/Public/CMS-NPI/20211214/pl_pfile_20050523-20211212.csv.gz"
    )
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

env.Command(
  target=[
    "scratch/analysis/epa-frs.csv"
  ],
  source=[
    "source/extract-epa-frs.py",
    os.path.join(
      sharepoint,
      "Data/Public/EPA/Facility Registry System/20220711/NATIONAL_SINGLE.CSV.gz"
    ),
    "scratch/lookups/national-blkgrp.dat"
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

env.Command(
  target=[
    "scratch/analysis/hud-phb.csv"
  ],
  source=[
    "source/extract-hud-phb.py",
    os.path.join(
      sharepoint,
      "Data/Public/HUD/Public Housing Buildings/20220711/Public_Housing_Buildings.csv"
    ),
    "scratch/lookups/national-blkgrp.dat"
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

env.Command(
  target=[
    "scratch/analysis/uspto-pat.csv"
  ],
  source=[
    "source/extract-uspto-pat.py",
    os.path.join(
      sharepoint,
      "Data/Public/USPTO/Patent Assignment Dataset/2020/assignment.csv.gz"
    ),
    os.path.join(
      sharepoint,
      "Data/Public/USPTO/Patent Assignment Dataset/2020/assignee.csv.gz"
    )
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

env.Command(
  target=[
    "scratch/analysis/uspto-tm.csv"
  ],
  source=[
    "source/extract-uspto-tm.py",
    os.path.join(
      sharepoint,
      "Data/Public/USPTO/Trademark Assignment Dataset/2020/tm_assignment.csv.gz"
    ),
    os.path.join(
      sharepoint,
      "Data/Public/USPTO/Trademark Assignment Dataset/2020/tm_assignee.csv.gz"
    )
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

# Censuscode test data with line, point, and all lookups

tests = {
  "cms-npi": "year",
  "epa-frs": "year blkgrp_true",
  "hud-phb": "year blkgrp_true",
  "uspto-pat": "year",
  "uspto-tm": "year"
}

for test in tests:
  for lookup in ["line", "point", "all"]:
    cols = tests[test]
    env.Command(
      target=[
        f"scratch/analysis/censuscoded/{lookup}/{test}.csv"
      ],
      source=[
        f"scratch/analysis/{test}.csv",
        f"scratch/package/{lookup}/package.log"
      ],
      action=f"python -m censuscoding --data scratch/package/{lookup}/package --preserve-rows --preserve-cols {cols} -i $SOURCE -o $TARGET >${{TARGET}}.log"
    )

### Coverage validation ###

env.Command(
  target=[
    f"scratch/analysis/coverage.csv"
  ],
  source=[
    "source/coverage.py",
    "data/zip3.csv"
  ] + [
    f"scratch/analysis/censuscoded/{lookup}/{test}.csv"
    for lookup in ["line", "point", "all"]
    for test in tests
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

env.Command(
  target=[
    f"scratch/analysis/coverage.pdf"
  ],
  source=[
    "source/coverage-plot.R",
    "scratch/analysis/coverage.csv"
  ],
  action="Rscript $SOURCES $TARGET >${TARGET}.log"
)

### Accuracy validation ###

env.Command(
  target=[
    f"scratch/analysis/accuracy.csv"
  ],
  source=[
    "source/accuracy.py"
  ] + [
    f"scratch/analysis/censuscoded/{lookup}/{test}.csv"
    for lookup in ["line", "point", "all"]
    for test in ["epa-frs", "hud-phb"]
  ],
  action="python $SOURCES $TARGET >${TARGET}.log"
)

env.Command(
  target=[
    f"scratch/analysis/accuracy.pdf"
  ],
  source=[
    "source/accuracy-plot.R",
    "scratch/analysis/accuracy.csv"
  ],
  action="Rscript $SOURCES $TARGET >${TARGET}.log"
)

# vim: syntax=python expandtab sw=2 ts=2