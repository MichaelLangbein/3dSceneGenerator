import { describe, expect, it } from 'vitest';
import * as tf from '@tensorflow/tfjs';
import { readFileSync } from 'fs';
import modelUrl from '../data/graphModel/model.json?url';


console.log(modelUrl)
// const inputTensor = tf.zeros([1, 256, 256, 3]);
// const outputTensor = model.predict(inputTensor) as tf.Tensor<tf.Rank.R4>;
// const data = outputTensor.arraySync();
// console.log(data);


describe('tensorflow basics', () => {
    
    it('should import tf models', async () => {
        const model = await tf.loadGraphModel(modelUrl);
        expect(model).toBeTruthy();
    })

})