# Censuscoding Data

## Windows setup

Requires python 3.8 on Windows:

    scoop bucket add versions
    scoop install python38

Install required packages with:

    pip install -U pip setuptools wheel
    pip install pandas pyshp rtree scons shapely usaddress

## Build

Run `scons` in the root directory.
