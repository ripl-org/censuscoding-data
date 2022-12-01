# Censuscoding Data

## Windows setup

Requires python 3.8 on Windows:

    scoop bucket add versions
    scoop install python38

Install required packages with:

    pip install -U pip setuptools wheel
    pip install pandas pyshp rtree scons shapely usaddress==0.5.10

## Build

Run `scons` in the root directory.


## License

Data provided by permission of [King County] (https://www5.kingcounty.gov/sdc/addl_doc/KCGISCenterTermsAndConditions.pdf).
