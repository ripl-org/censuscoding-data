import json
import os

env = Environment(ENV=os.environ)
sharepoint = os.path.join(
  os.path.expanduser("~"),
  "Research Improving People's Lives",
  "RIPL All Staff - Documents"
)
states = json.load(open("states.json"))

env.CacheDir(os.path.join(sharepoint, "Data/Public/Censuscoding/scons-cache"))

for state, config in states.items():

  env.Depends(
    env.Command(
      target=[
        f"scratch/{state}/address.csv.gz",
        f"scratch/{state}/address.log"
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
      f"scratch/{state}/address-blkgrp.csv.gz",
      f"scratch/{state}/address-blkgrp.log"
    ],
    source=[
      "source/locate-blkgrp.py",
      os.path.join(sharepoint, config["blkgrp"]["path"]),
      f"scratch/{state}/address.csv.gz"
    ],
    action="python $SOURCES ${TARGETS[0]} >${TARGETS[1]}"
  )

  env.Command(
    target=[
      f"scratch/{state}/blkgrp-zip-street-names.csv",
      f"scratch/{state}/blkgrp-zip-street-nums.csv",
      f"scratch/{state}/blkgrp-zip.log"
    ],
    source=[
      "source/zip-lookups.py",
      f"scratch/{state}/address-blkgrp.csv.gz",
      Value("BlockGroup")
    ],
    action="python $SOURCES ${TARGETS[0]} ${TARGETS[1]} >${TARGETS[2]}"
  )

# vim: syntax=python expandtab sw=4 ts=4
