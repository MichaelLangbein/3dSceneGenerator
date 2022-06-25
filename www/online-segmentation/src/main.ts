import './style.css'
import 'ol/ol.css';
import { Map, View } from 'ol';
import { Tile as TileLayer } from 'ol/layer';
import WebGLTileLayer from 'ol/layer/WebGLTile';
import { OSM, GeoTIFF } from 'ol/source';
import { ScaleLine, Zoom, MousePosition, Attribution } from 'ol/control';
import cogUrl from '../data/s2/TCI.tif?url';
import { getViewParas } from './utils';
import RasterSource from 'ol/source/Raster';
import ImageLayer from 'ol/layer/Image';
// const cogUrl = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/U/PU/2022/6/S2B_32UPU_20220612_0_L2A/TCI.tif";





const viewParameters = getViewParas('EPSG:4326');

const container = document.getElementById('map');

const osmLayer = new TileLayer({
    source: new OSM()
})


const s2Layer = new WebGLTileLayer({
    source: new GeoTIFF({
        sources: [{
            url: cogUrl,
        }],
    })
})

function isImageData(input: any): input is ImageData {
    return input.hasOwnProperty('data');
}

const segmentedLayer = new ImageLayer({
    source: new RasterSource({
        sources: [s2Layer.getSource()!],
        operationType: 'image',
        operation: function(inputImages: ImageData[] | number[][]): ImageData {
            if (!isImageData(inputImages[0])) throw Error();

            const inputImage: ImageData = inputImages[0];
            return inputImage;
        }
    })
});

const layers = [osmLayer, s2Layer];

const view = new View(viewParameters);

const controls = [new ScaleLine(), new Zoom(), new MousePosition(), new Attribution()];

const map = new Map({
    target: container!,
    layers: layers,
    view: view,
    controls: controls,
});