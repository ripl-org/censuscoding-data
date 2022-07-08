import json
import os

env = Environment(ENV=os.environ)
sharepoint = os.path.join(
  os.path.expanduser("~"),
  "Research Improving People's Lives",
  "RIPL All Staff - Documents"
)
states = json.load(open("states.json"))

#env.CacheDir(os.path.join(sharepoint, "Data/Public/Censuscoding/scons-cache"))

# State lookups

for state, config in states.items():

  env.Depends(
    env.Command(
      target=[
        f"scratch/lookups/{state}/address.csv.gz",
        f"scratch/lookups/{state}/address.log"
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
      f"scratch/lookups/{state}/address-blkgrp.csv.gz",
      f"scratch/lookups/{state}/address-blkgrp.log"
    ],
    source=[
      "source/locate-blkgrp.py",
      os.path.join(sharepoint, config["blkgrp"]["path"]),
      f"scratch/lookups/{state}/address.csv.gz"
    ],
    action="python $SOURCES ${TARGETS[0]} >${TARGETS[1]}"
  )

  env.Command(
    target=[
      f"scratch/lookups/{state}/lookup-street.csv.gz",
      f"scratch/lookups/{state}/lookup-street-num.csv.gz",
      f"scratch/lookups/{state}/lookup-street.log"
    ],
    source=[
      "source/build-lookups.py",
      f"scratch/lookups/{state}/address-blkgrp.csv.gz",
      Value("BlockGroup")
    ],
    action="python $SOURCES ${TARGETS[0]} ${TARGETS[1]} >${TARGETS[2]}"
  )

# Merge and package lookups

env.Command(
  target=[
    "scratch/lookups/street.json.gz"
  ],
  source=(
    ["source/merge-lookups-street.py"] +
    [f"scratch/lookups/{state}/lookup-street.csv.gz" for state in states]
  ),
  action="python $SOURCES $TARGET"
)

env.Command(
  target=[
    "scratch/lookups/street-num.json.gz"
  ],
  source=(
    [
      "source/merge-lookups-street-num.py", 
      "scratch/lookups/street.json.gz"
    ] +
    [f"scratch/lookups/{state}/lookup-street-num.csv.gz" for state in states]
  ),
  action="python $SOURCES $TARGET"
)

env.Command(
  target=[
    "scratch/package.log"
  ],
  source=[
    "source/package-lookups.py",
    "scratch/lookups/street-num.json.gz"
  ],
  action="python $SOURCES $TARGET"
)

# Analysis data

env.Command(
  target=[
    "scratch/analysis/npi-addresses.csv"
  ],
  source=[
    "source/extract-npi-addresses.py",
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
    "scratch/analysis/uspto-pat-addresses.csv"
  ],
  source=[
    "source/extract-uspto-pat-addresses.py",
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
    "scratch/analysis/uspto-tm-addresses.csv"
  ],
  source=[
    "source/extract-uspto-tm-addresses.py",
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

for test in ["npi", "uspto-pat", "uspto-tm"]:
  env.Command(
    target=[
      f"scratch/analysis/{test}-addresses-censuscoded.csv"
    ],
    source=[
      f"scratch/analysis/{test}-addresses.csv"
    ],
    action="censuscoding -i $SOURCE -o $TARGET >${TARGET}.log"
  )

# vim: syntax=python expandtab sw=2 ts=2
