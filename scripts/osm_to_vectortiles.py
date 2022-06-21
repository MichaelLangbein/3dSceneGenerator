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


#%% Part 0: directories
thisDir = os.getcwd()
assetDir = os.path.join(thisDir, '..', 'data')
vectorTileDir = os.path.join(assetDir, 'vectorTiles')
os.makedirs(vectorTileDir, exist_ok=True)


#%%

def downloadPbf(dataUrl):
    response = req.get(dataUrl)
    fileName = urlparse(dataUrl).path.split('/').pop()
    path = os.path.join(vectorTileDir, fileName)
    with open(path, 'wb') as fh:
        fh.write(response.content)
    return path


def pbf2mbt(pbfPath):



def createVectorTiles(dataUrl):
    print(f"Downloading {dataUrl} ...")
    pbf = downloadPbf(dataUrl)
    mbt = pbf2mbt(pbf)
    pyramidDir = mbt2xyz(mbt)




    

#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads OSM data and converts it into vector-tiles')
    parser.add_argument('--data', required=True, type=str, help='Url to pbf files. Example: --data https://download.geofabrik.de/europe/germany/bayern/oberfranken-latest.osm.pbf')

    args = parser.parse_args()

    createVectorTiles(args.data)

