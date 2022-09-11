# https://dwtkns.com/srtm30m/
# <- requires sign-in
# http://opendemdata.info/data/europe_laea/N290E425.zip
# <- in 0.5 degree-steps

#%% imports
import os
import argparse as ap
import requests as req
import numpy as np

#%% Part 0: directories
thisDir = os.getcwd()
assetDir = os.path.realpath(os.path.join(thisDir, 'data'))
srtmDir = os.path.join(assetDir, 'srtm')
os.makedirs(srtmDir, exist_ok=True)



#%% Part 1: download osm data


def fileExists(path):
    return os.path.exists(path)


def downloadFile(url, targetDir, fileName):
    r = req.get(url)
    with open(os.path.join(targetDir, fileName),'wb') as output_file:
        output_file.write(r.content)



def downloadSrtmData(user, password, dataDir, bbox):

    northMin = int(np.floor(bbox[1]))
    northMax = int(np.floor(bbox[3]))
    eastMin  = int(np.floor(bbox[0]))
    eastMax  = int(np.floor(bbox[2]))

    for n in range(northMin, northMax + 1):
        for e in range(eastMin, eastMax + 1):
            if len(str(e)) == 2:
                e = f"0{e}"
            fileName = f"N{n}E{e}.SRTMGL1.hgt.zip"
            if not fileExists(os.path.join(dataDir, fileName)):
                url = f"https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/{fileName}"
                print(url)
                # downloadFile(url, dataDir, fileName)
                
    
 


#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads SRTM data')
    parser.add_argument('--username', required=True, type=str, help='Your https://urs.earthdata.nasa.gov/profile user-name')
    parser.add_argument('--password', required=True, type=str, help='Your https://urs.earthdata.nasa.gov/profile password')
    parser.add_argument('--data-dir', required=False, type=str, default=srtmDir, help='directory where downloaded data should be kept')
    parser.add_argument('--bbox', required=True, type=float, nargs=4, help='Bbox in EPSG:4326. Space separated list. Example: --bbox 11.21309 48.0658 11.30064 48.0916')

    args = parser.parse_args()

    downloadSrtmData(args.username, args.password, args.data_dir, args.bbox)
