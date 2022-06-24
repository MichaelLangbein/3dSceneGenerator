#%% imports
import os
import argparse as ap
import requests as req
from urllib.parse import urlparse

from pystac_client import Client
import rasterio as rio
from pyproj.transformer import Transformer


#%% Part 0: directories
thisDir = os.getcwd()
assetDir = os.path.realpath(os.path.join(thisDir, 'data'))
sentinelDir = os.path.join(assetDir, 'sentinel')
os.makedirs(sentinelDir, exist_ok=True)



#%% Part 1: download S2 data

def createFilePath(itemId, itemHref):
    itemDir = os.path.join(sentinelDir, itemId)
    url = urlparse(itemHref)
    fileName = os.path.basename(url.path)
    os.makedirs(itemDir, exist_ok=True)
    return os.path.join(itemDir, fileName)


def downloadSentinelData(bbox, maxItems, maxCloudCover):
    catalog = Client.open("https://earth-search.aws.element84.com/v0")
    searchResults = catalog.search(
        collections=['sentinel-s2-l2a-cogs'],
        bbox=bbox,
        max_items=maxItems,
        query={
            "eo:cloud_cover":{"lt":maxCloudCover},
            "sentinel:valid_cloud_cover": {"eq": True}
        },
    )
    
    for item in searchResults.get_items():
        for key, val in item.assets.items():

            if val.href.endswith('tif'):
                print(f"Reading {val.href} ...")

                with rio.open(val.href) as fh:
                    coordTransformer = Transformer.from_crs('EPSG:4326', fh.crs)
                    coordUpperLeft = coordTransformer.transform(bbox[3], bbox[0])
                    coordLowerRight = coordTransformer.transform(bbox[1], bbox[2]) 
                    pixelUpperLeft = fh.index( coordUpperLeft[0],  coordUpperLeft[1] )
                    pixelLowerRight = fh.index( coordLowerRight[0],  coordLowerRight[1] )
                    # make http range request only for bytes in window
                    # bands = list(range(1, fh.meta['count'] + 1))
                    window = rio.windows.Window.from_slices(
                        ( pixelUpperLeft[0],  pixelLowerRight[0] ), 
                        ( pixelUpperLeft[1],  pixelLowerRight[1] )
                    )
                    subset = fh.read(window=window)

                    fileParas = fh.meta
                    fileParas.update({
                        "driver": "GTiff",
                        "count": subset.shape[0],
                        "height": subset.shape[1],
                        "width": subset.shape[2],
                    })

                    filePath = createFilePath(item.id, val.href)
                    with rio.open(filePath, "w", **fileParas) as dest:
                        print(f"Saving to {filePath} ...")
                        dest.write(subset)
                    

    print("Done!")
#%%
bbox = [11.3, 48.0, 11.4, 48.1]
downloadSentinelData(bbox, 1, 5)


#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads S2 data')
    
    parser.add_argument('--bbox', type=float, nargs=4, help='Bbox in EPSG:4326. Space separated list. Example: --bbox 11.21309 48.0658 11.30064 48.0916')
    parser.add_argument('--max-items', type=int, default=4, help='Maximum number of datasets to download')
    parser.add_argument('--max-cloud', type=int, default=10, help='Maximum cloud coverage (integer between 0 and 100)')

    args = parser.parse_args()

    downloadSentinelData(args.bbox, args.maxItems, args.maxCloudCover)



