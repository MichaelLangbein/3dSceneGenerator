import numpy as np
from IPython.display import Image, display
import os
from PIL.ImageOps import autocontrast
from datetime import datetime
from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img, array_to_img


def displayColorImage(path):
    img = Image(filename=path)
    display(img)

def displaySegmentImage(path):
    # Display auto-contrast version of corresponding target (per-pixel categories)
    img = autocontrast(load_img(path))
    display(img)

def displaySegmentData(data):
    mask = np.argmax(data, axis=-1)
    mask = np.expand_dims(mask, axis=-1)
    img = autocontrast(array_to_img(mask))
    display(img)


def saveModel(model: keras.Model, path: str, modelName: str):
    fullPath = os.path.join(path, modelName + '_' + datetime.now().strftime("%d.%m.%Y_%H:%M:%S") )
    model.save(fullPath)

def loadModel(path: str):
    return keras.models.load_model(path)