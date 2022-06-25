#! /bin/bash

fileName=$1
gdalwarp -s_srs EPSG:3857 -t_srs EPSG:4326 $fileName $fileName