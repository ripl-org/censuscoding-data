import os

env = Environment(ENV=os.environ)

env.AlwaysBuild(
  env.Command("public-data/all",
              ["source/unzip-public-data.py",
               "public-data-paths.json",
               Value("RI")],
              "python $SOURCES $TARGETS")
)

env.Command("scratch/e911.csv",
            ["source/clean.py",
             "public-data/E-911_Sites.csv",
             "data/StreetTypes.csv"],
            "python $SOURCES $TARGETS")

env.Command("scratch/e911-blocks.csv",
            ["source/blocks.py",
             "public-data/tl_2020_44_tabblock20.shp",
             "scratch/e911.csv"],
            "python $SOURCES $TARGET")

env.Command(["scratch/blkgrp-city-street-names.csv",
             "scratch/blkgrp-city-street-nums.csv"],
            ["source/city-lookups.py",
             "scratch/e911-blocks.csv",
             Value("BlockGroup")],
            "python $SOURCES $TARGETS")

env.Command(["scratch/blkgrp-zip-street-names.csv",
             "scratch/blkgrp-zip-street-nums.csv"],
            ["source/zip-lookups.py",
             "scratch/e911-blocks.csv",
             Value("BlockGroup")],
            "python $SOURCES $TARGETS")

env.Command(["scratch/tract-city-street-names.csv",
             "scratch/tract-city-street-nums.csv"],
            ["source/city-lookups.py",
             "scratch/e911-blocks.csv",
             Value("Tract")],
            "python $SOURCES $TARGETS")

env.Command(["scratch/tract-zip-street-names.csv",
             "scratch/tract-zip-street-nums.csv"],
            ["source/zip-lookups.py",
             "scratch/e911-blocks.csv",
             Value("Tract")],
            "python $SOURCES $TARGETS")

env.Command(["scratch/blkgrp-centroids.csv"],
            ["source/centroids.py",
             "public-data/cb_2020_44_bg_500k.shp"],
            "python $SOURCES $TARGETS")

env.Command(["scratch/blkgrp-distance.csv"],
            ["source/distance.py",
             "scratch/blkgrp-centroids.csv"],
            "python $SOURCES $TARGETS")

# vim: syntax=python expandtab sw=4 ts=4
