#!/bin/bash

wget --no-parent --no-directories -e robots=off --reject "index.html*" --recursive  https://www.ngdc.noaa.gov/mgg/gravity/1999/data/regional/calif/ --directory-prefix calif
