#%% imports
import os
import argparse as ap
import requests as req
import json

import osm2geojson as o2g


#%% Part 0: directories
thisDir = os.getcwd()
assetDir = os.path.join(thisDir, '..', 'data')
overpassDir = os.path.join(assetDir, 'overpass')
os.makedirs(overpassDir, exist_ok=True)



#%% Part 1: download osm data

def downloadOsmData(bbox, queries):
    stringifiedBbox = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"
    
    buildingQuery = f"""
        [out:json];     /* output in json format */
        way[building]( {stringifiedBbox} );
        (._;>;);        /* get the nodes that make up the ways  */
        out geom;
    """
    
    treesQuery = f"""
    [out:json];
    (
        way[landuse=forest]( {stringifiedBbox} );
        way[landuse=meadow]( {stringifiedBbox} );
        way[landuse=orchard]( {stringifiedBbox} );
    );              /* union of the above statements */
    (._;>;);
    out geom;
    """
    
    waterQuery = f"""
    [out:json];
    way[natural=water]( {stringifiedBbox} );
    (._;>;);
    out geom;
    """
    
    namedQueries = {
        'buildings': buildingQuery,
        'trees': treesQuery,
        'water': waterQuery
    }
    
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    for name, query in namedQueries.items():
        if name in queries:
            print(f"Executing {name} query...")
            response = req.get(overpass_url, params={'data': query})
            jsonData = response.json()
            geoJsonData = o2g.json2geojson(jsonData)
            # @TODO: filter out single nodes. We only care about polygons.
            filePath = os.path.join(overpassDir, name + '.geo.json')
            with open(filePath, 'w') as fh:
                json.dump(geoJsonData, fh, indent=4)
    print("Done!")

#%%
if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Downloads OSM data through a selection of pre-defined overpass-queries')
    parser.add_argument('--bbox', required=True, type=float, nargs=4, help='Bbox in EPSG:4326. Space separated list. Example: --bbox 11.21309 48.0658 11.30064 48.0916')
    parser.add_argument('--queries', required=True, type=str, nargs='+', help='Types of data to query. Must be last argument used. Example: --queries buildings water trees')

    args = parser.parse_args()

    downloadOsmData(args.bbox, args.queries)
