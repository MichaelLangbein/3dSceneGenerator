# https://dwtkns.com/srtm30m/
# <- requires sign-in
# http://opendemdata.info/data/europe_laea/N290E425.zip
# <- in 0.5 degree-steps
# https://github.com/bopen/elevation


#%% imports
import os
import argparse as ap
import elevation as e


#%% Part 0: directories
thisDir = os.getcwd()
assetDir = os.path.realpath(os.path.join(thisDir, 'data'))
srtmDir = os.path.join(assetDir, 'srtm')
os.makedirs(srtmDir, exist_ok=True)



#%% Part 1: download srtm data

def downloadSrtmData(dataDir, bbox):
    fileName = '_'.join([str(c) for c in bbox]) + '.tif'
    outFile = os.path.join(dataDir, fileName)
    e.clip(bounds=bbox, output=outFile)
    e.clean()


#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads SRTM data')
    parser.add_argument('--data-dir', required=False, type=str,   default=srtmDir, help='directory where downloaded data should be kept'                                             )
    parser.add_argument('--bbox',     required=True,  type=float, nargs=4,         help='Bbox in EPSG:4326. Space separated list. Example: --bbox 11.21309 48.0658 11.30064 48.0916' )

    args = parser.parse_args()

    downloadSrtmData(args.data_dir, args.bbox)
