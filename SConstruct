import json
import os

env = Environment(ENV=os.environ)
sharepoint = os.path.join(
  os.path.expanduser("~"),
  "Research Improving People's Lives",
  "RIPL All Staff - Documents"
)
states = json.load(open("states.json"))

for state, config in states.items():

  env.Command(
    target=[
      f"scratch/{state}/address.csv"
    ],
    source=[
      "source/clean-{}.py".format(config["address"]["method"]),
      os.path.join(sharepoint, config["address"]["path"])
    ],
    action="python $SOURCES $TARGETS"
  )

  env.Command(
    target=[
      f"scratch/{state}/address-blkgrp.csv",
    ],
    source=[
      "source/locate-blkgrp.py",
      os.path.join(sharepoint, config["blkgrp"]["path"]),
      f"scratch/{state}/address.csv"
    ],
    action="python $SOURCES $TARGET"
  )

  env.Command(
    target=[
      f"scratch/{state}/blkgrp-zip-street-names.csv",
      f"scratch/{state}/blkgrp-zip-street-nums.csv"
    ],
    source=[
      "source/zip-lookups.py",
      f"scratch/{state}/address-blkgrp.csv",
      Value("BlockGroup")
    ],
    action="python $SOURCES $TARGETS"
  )

# vim: syntax=python expandtab sw=4 ts=4
