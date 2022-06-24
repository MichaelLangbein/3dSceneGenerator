#%%
import os
import random
from loader import SegmentationDataLoader
import image_slicer as imsl
from transformers import pipeline

#%%
# background – 1
# building – 2
# road – 3
# water – 4
# barren – 5
# forest – 6
# agriculture – 7
# And the no-data regions were assigned 0 which should be ignored
# Missing data should be ok: https://stackoverflow.com/questions/52570199/multivariate-lstm-with-missing-values

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, 'data/sats/Train')
INPUT_DIR1 = os.path.join(DATA_DIR, 'Urban/images_png')
TARGET_DIR1 = os.path.join(DATA_DIR, 'Urban/masks_png')
INPUT_DIR2 = os.path.join(DATA_DIR, 'Rural/images_png')
TARGET_DIR2 = os.path.join(DATA_DIR, 'Rural/masks_png')
MODEL_DIR = os.path.join(DATA_DIR, 'trained_models')
MODEL_NAME = 'hugging'
IMAGE_SIZE = (512, 512)
NUM_CLASSES = 8
BATCH_SIZE = 32


#%%
for dirPath, dirNames, fileNames in os.walk(DATA_DIR):
    for fileName in fileNames:
        if fileName.endswith('.png') and '_' not in fileName:
            fullName = os.path.join(dirPath, fileName)
            imsl.slice(fullName, 4)
            os.remove(fullName)


#%%
input_img_paths = []
target_img_paths = []

inputDir1Contents = [file for file in os.listdir(INPUT_DIR1) if '_' in file and file.endswith('.png')]
inputDir2Contents = [file for file in os.listdir(INPUT_DIR2) if '_' in file and file.endswith('.png')]
targetDir1Contents = [file for file in os.listdir(TARGET_DIR1) if '_' in file and file.endswith('.png')]
targetDir2Contents = [file for file in os.listdir(TARGET_DIR2) if '_' in file and file.endswith('.png')]

for sourceName in inputDir1Contents:
    if sourceName in targetDir1Contents:
        input_img_paths.append(os.path.join(INPUT_DIR1, sourceName))
        target_img_paths.append(os.path.join(TARGET_DIR1, sourceName))
for sourceName in inputDir2Contents:
    if sourceName in targetDir2Contents:
        input_img_paths.append(os.path.join(INPUT_DIR2, sourceName))
        target_img_paths.append(os.path.join(TARGET_DIR2, sourceName))



#%%
# Split our img paths into a training and a validation set
val_samples = 1000
random.Random(1337).shuffle(input_img_paths)
random.Random(1337).shuffle(target_img_paths)
train_input_img_paths = input_img_paths[:-val_samples]
train_target_img_paths = target_img_paths[:-val_samples]
val_input_img_paths = input_img_paths[-val_samples:]
val_target_img_paths = target_img_paths[-val_samples:]

# Instantiate data Sequences for each split
train_gen = SegmentationDataLoader(BATCH_SIZE, IMAGE_SIZE, train_input_img_paths, train_target_img_paths)
val_gen   = SegmentationDataLoader(BATCH_SIZE, IMAGE_SIZE, val_input_img_paths, val_target_img_paths)


#%%
segmenter = pipeline("image-segmentation")
