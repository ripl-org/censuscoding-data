# Censuscoding Data

## License

Copyright 2021-2023 Innovative Policy Lab d/b/a Research Improving People's Lives
("RIPL"), Providence, RI. All Rights Reserved.

Your use of the Software License along with any related Documentation, Data,
etc. is governed by the terms and conditions which are available here:
[LICENSE.md](https://github.com/ripl-org/censuscoding-data/blob/main/LICENSE.md)

Please contact [connect@ripl.org](mailto:connect@ripl.org) to inquire about
commercial use.

## Build Steps

This tool uses the [scons](https://scons.org/) build system. The sequence of
build steps and intermediary files are described in the included
[SConstruct](https://github.com/ripl-org/censuscoding-data/blob/main/SConstruct) file.

First, install the python (>=3.10) build dependencies with:

    pip install numpy pandas pyshp rtree scipy scons shapely usaddress zenodo-get

Next, install the R (>=4.2) plotting dependencies with:

    Rscript -e 'install.packages(c("tidyverse", "ggplot2", "viridis", "ggsci", "gridExtra", "devtools"), repos = c("https://cran.r-project.org"))'
    Rscript -e 'require("devtools"); devtools::install_github("UrbanInstitute/urbnmapr")'

Finally, run the `scons` command from the root directory to start the build.
You can instead use `scons -n` for a dry run or `scons -jN` to run on *N*
concurrent processors.

##

Zip/county crosswalk from https://www.huduser.gov/portal/datasets/usps_crosswalk.html