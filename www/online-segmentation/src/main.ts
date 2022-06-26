import './style.css'
import * as tf from '@tensorflow/tfjs';
import { interpolateYlGn } from 'd3-scale-chromatic';
import { rgb } from 'd3-color';

import modelUrl from '../data/graphModel/model.json?url';




const inputImage = document.getElementById('inputImage') as HTMLImageElement;
const outputImage = document.getElementById('outputImage') as HTMLCanvasElement;
const analyzeButton = document.getElementById('analyze') as HTMLButtonElement;

const model = await tf.loadGraphModel(modelUrl);



async function analyzeImage() {

    console.log('Starting ...');

    const outputData = tf.tidy(() => {
        const inputTensor = tf.browser.fromPixels(inputImage);
        const inputTensorF32 = tf.tensor(inputTensor.dataSync(), inputTensor.shape, 'float32');
        const inputTensor4d = tf.reshape(inputTensorF32, [1, ... inputTensor.shape]);
        const outputTensor = model.predict(inputTensor4d) as tf.Tensor<tf.Rank.R4>;
        const outputData = outputTensor.arraySync();
        return outputData[0];
    });
    
    console.log('Creating output image ...')

    const w = inputImage.width;
    const h = inputImage.height;
    const imageData: Uint8ClampedArray = new Uint8ClampedArray(w * h * 4);
    for (let r = 0; r < outputData.length; r++) {
        const row = outputData[r];
        for (let c = 0; c < row.length; c++) {
            const pixelData = row[c];
            const color = pixData2Color(pixelData);
            imageData[(r*w + c)*4 + 0] = color[0];
            imageData[(r*w + c)*4 + 1] = color[1];
            imageData[(r*w + c)*4 + 2] = color[2];
            imageData[(r*w + c)*4 + 3] = color[3];
        }
    }
    const outputImageData = new ImageData(imageData, inputImage.width, inputImage.height);
    outputImage.width = outputImageData.width;
    outputImage.height = outputImageData.height;
    const ctx = outputImage.getContext('2d');
    ctx?.putImageData(outputImageData, 0, 0);

    console.log('... done!');
    console.log(outputImageData);
}


analyzeButton.addEventListener('click', analyzeImage);





function maxVal(data: number[]): number {
    let maxI = 0;
    let maxVal = -99999999;
    for (let i = 0; i < data.length; i++) {
        if (data[i] > maxVal) {
            maxI = i;
            maxVal = data[i];
        }
    }
    return maxI;
}

function pixData2Color(pixelData: number[]): [number, number, number, number] {
    const colorIndex = maxVal(pixelData);
    const colorName = interpolateYlGn(colorIndex / 7);
    const colorObj = rgb(colorName);
    return [colorObj.r, colorObj.g, colorObj.b, 256];
}
