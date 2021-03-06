"""
1. Download data
    - free:
        - source: geofabrik
        - convert osm.pbf to mbtiles: tilemaker (https://github.com/systemed/tilemaker)
    - paid: 
        - openmaptiles (one-time-pay)
2. extract data
    2.1. mb-util: `mb-util --scheme=xyz --image_format=pbf 2017-07-03_germany_bamberg.mbtiles extractedDir`
    2.2. rename: `find . -name '*.gz' -exec mv '{}' '{}'.gz  \;`
    2.3. extract: ` find . -name '*.gz' -exec gunzip '{}' \;`  (otherwise Error: Unimplemented type: 3)
3. Download style
    - https://openmaptiles.org/styles/
4. Edit style
    4.1. tiles & fonts:
        ```json
                "sources": {
                "openmaptiles": {
                    "type": "vector",
                    "tiles": ["http://localhost:8080/assets/extracted/{z}/{x}/{y}.pbf"]
                    }
                },
                "glyphs": "http://localhost:8080/assets/fonts/{fontstack}/{range}.pbf",
        ```
5. Download fonts:
    - https://blog.kleunen.nl/blog/tilemaker-generate-map
6. Display on map
    6.1. Must be same projection: EPSG:3857
    6.2. Data must not be gzipped
"""

#%% imports
import os
import argparse as ap
import requests as req
from urllib.parse import urlparse
import shutil as shu

import mbutil as mb
from utils import downloadFromUrlTo, replaceInFile


#%% Part 0: directories
thisDir = os.getcwd()
tileMakerDir = os.path.join(thisDir, 'tilemaker')
assetDir = os.path.realpath(os.path.join(thisDir, 'data'))
tmpDir = os.path.join(assetDir, 'tmp')
vectorTileDir = os.path.join(assetDir, 'vectorTiles')
os.makedirs(vectorTileDir, exist_ok=True)
os.makedirs(tmpDir, exist_ok=True)


#%%




def downloadAdditionalData():
    downloadFromUrlTo(
        os.path.join(tileMakerDir, 'coastline'),
        'https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip'
    )


def downloadPbf(dataUrl):
    fileName = urlparse(dataUrl).path.split('/').pop()
    path = os.path.join(tmpDir, fileName)
    if os.path.exists(path):
        print(f"Already downloaded {path}.")
        return path
    response = req.get(dataUrl)
    with open(path, 'wb') as fh:
        fh.write(response.content)
    return path


def pbf2mbt(pbfPath):
    mbtPath = pbfPath.replace('pbf', 'mbtiles')
    if os.path.exists(mbtPath):
        print(f"Already exists: {mbtPath}.")
        return mbtPath
    result = os.system(f"{tileMakerDir}/tilemaker --input {pbfPath} --output {mbtPath} --process {tileMakerDir}/config/process-openmaptiles.lua --config {thisDir}/tilemaker/config/config-openmaptiles.json")
    return mbtPath


def mbt2xyz(mbtPath):
    pyramidDir = os.path.join(vectorTileDir, 'xyz')
    if os.path.exists(pyramidDir):
        shu.rmtree(pyramidDir)
    mb.mbtiles_to_disk(mbtPath, pyramidDir, scheme='xyz', format='pbf')
    return pyramidDir


def copyFonts():
    fontDir = os.path.join(tileMakerDir, 'fonts')
    fontTargetDir = os.path.join(vectorTileDir, 'fonts')
    shu.copytree(fontDir, fontTargetDir, dirs_exist_ok=True)


def copyStyle(style):
    styleFile = os.path.join(tileMakerDir, 'styles', style + '.json')
    shu.copy(styleFile, vectorTileDir)


def createVectorTiles(dataUrl, style, hostedAt):
    print(f"Downloading {dataUrl} ...")
    pbf = downloadPbf(dataUrl)
    print(f"Converting to mbt ...")
    mbt = pbf2mbt(pbf)
    print(f"Creating pyramid ...")
    pyramidDir = mbt2xyz(mbt)
    print(f"Copying fonts ...")
    copyFonts()
    print(f"Copying style: {style} ...")
    newStyleLocation = copyStyle(style)
    replaceInFile(newStyleLocation, r'{{HOSTED_URL}}', hostedAt)
    print("Done!")




    

#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads OSM data and converts it into vector-tiles')
    parser.add_argument('--data', required=True, type=str, help='Url to pbf files. Example: --data https://download.geofabrik.de/europe/germany/bayern/oberfranken-latest.osm.pbf')
    parser.add_argument('--style', required=True, type=str, help='Name of style-file to use. Possible values: basic, 3d, positron, terrain')
    parser.add_argument('--hosted-at', required=True, type=str, help='Under which url will data be hosted? Example: http://localhost:8080/assets/')

    args = parser.parse_args()

    createVectorTiles(args.data, args.style, args.hosted_at)

