import './style.css'
import 'ol/ol.css';
import { Map, View } from 'ol';
import { Tile as TileLayer } from 'ol/layer';
import WebGLTileLayer from 'ol/layer/WebGLTile';
import { OSM, GeoTIFF } from 'ol/source';
import { ScaleLine, Zoom, MousePosition, Attribution } from 'ol/control';
import { getViewParas } from './utils';
import RasterSource from 'ol/source/Raster';
import ImageLayer from 'ol/layer/Image';
import * as tf from '@tensorflow/tfjs';



// const cogUrl = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/U/PU/2022/6/S2B_32UPU_20220612_0_L2A/TCI.tif";
import cogUrl from '../data/s2/TCI.tif?url';
import modelUrl from '../data/graphModel/model.json?url';





const model = await tf.loadGraphModel(modelUrl);
// const inputTensor = tf.zeros([1, 256, 256, 3]);
// const outputTensor = model.predict(inputTensor) as tf.Tensor<tf.Rank.R4>;
// const data = outputTensor.arraySync();
// console.log(data);


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

            const outputData = tf.tidy(() => {
                const inputTensor = tf.browser.fromPixels(inputImage);
                const inputTensor4d = tf.reshape(inputTensor, [1, ... inputTensor.shape]);
                const outputTensor = model.predict(inputTensor4d) as tf.Tensor<tf.Rank.R4>;
                const outputData = outputTensor.arraySync();
                return outputData[0];
            });

            const classNr = 7;

            const w = inputImage.width;
            const h = inputImage.height;
            const imageData: Uint8ClampedArray = new Uint8ClampedArray(w * h * 4);
            for (let r = 0; r < outputData.length; r++) {
                const row = outputData[r];
                for (let c = 0; c < row.length; c++) {
                    const pixelData = row[c];
                    const classIntensity = pixelData[classNr];
                    const color = Math.round(classIntensity * 255);
                    imageData[r*w + c*4 + 0] = color;
                    imageData[r*w + c*4 + 1] = color;
                    imageData[r*w + c*4 + 2] = color;
                    imageData[r*w + c*4 + 3] = color;
                }
            }
            const outputImage = new ImageData(imageData, inputImage.width, inputImage.height);
            return outputImage;
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

