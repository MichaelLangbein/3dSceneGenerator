#%% imports
import os
import argparse as ap
import requests as req
from urllib.parse import urlparse

from pystac_client import Client
import rasterio as rio
import rasterio.warp as riow # import calculate_default_transform, reproject, Resampling
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


def reprojectFile(sourceFilePath, targetFilePath, destinationProjection):
    with rio.open(sourceFilePath) as src:
        transform, width, height = riow.calculate_default_transform(
            src.crs, destinationProjection, 
            src.width, src.height, *src.bounds)
        
        kwargs = src.meta.copy()
        kwargs.update({
            'crs':       destinationProjection,
            'transform': transform,
            'width':     width,
            'height':    height
        })

        with rio.open(targetFilePath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                riow.reproject(
                    source          = rio.band(src, i),
                    destination     = rio.band(dst, i),
                    src_transform   = src.transform,
                    src_crs         = src.crs,
                    dst_transform   = transform,
                    dst_crs         = destinationProjection,
                    resampling      = riow.Resampling.nearest
                )


def downloadSentinelData(bbox, maxItems = 4, maxCloudCover = 10, targetProjectionCode = 4326):
    targetProjection = f"EPSG:{targetProjectionCode}"

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

                    coordTransformer = Transformer.from_crs(targetProjection, fh.crs)
                    [top,      right  ] = coordTransformer.transform(bbox[3], bbox[2])
                    [bottom,   left   ] = coordTransformer.transform(bbox[1], bbox[0]) 
                    [topPx,    rightPx] = fh.index(top,   right )
                    [bottomPx, leftPx ] = fh.index(bottom, left )

                    # make http range request only for bytes in window
                    window = rio.windows.Window.from_slices(
                        ( topPx,  bottomPx ), 
                        ( leftPx,  rightPx )
                    )
                    subset = fh.read(window=window)

                    fileParas = fh.meta
                    fileParas.update({
                        "driver":    "GTiff",
                        "count":     subset.shape[0],
                        "height":    subset.shape[1],
                        "width":     subset.shape[2],
                        "transform": fh.window_transform(window)
                    })

                    filePath = createFilePath(item.id, val.href)
                    with rio.open(filePath, "w", **fileParas) as dest:
                        dest.write(subset)

                    transformedFilePath = createFilePath(item.id + f"_{targetProjection}", val.href)
                    print(f"Saving to {transformedFilePath} ...")
                    reprojectFile(filePath, transformedFilePath, targetProjection)

    
    print("Done!")


#%%
bbox = [11.3, 48.0, 11.4, 48.1]
downloadSentinelData(bbox, 1, 5)


#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads S2 data')
    
    parser.add_argument('--bbox', type=float, nargs=4, help='Bbox in target-projection (4326 per default). Space separated list. Example: --bbox 11.21309 48.0658 11.30064 48.0916')
    parser.add_argument('--max-items', type=int, default=4, help='Maximum number of datasets to download')
    parser.add_argument('--max-cloud', type=int, default=10, help='Maximum cloud coverage (integer between 0 and 100)')
    parser.add_argument('--target-projection', type=int, default=4326, help='EPSG-code for target projection')

    args = parser.parse_args()

    downloadSentinelData(args.bbox, args.maxItems, args.maxCloudCover, args.targetProjection)



