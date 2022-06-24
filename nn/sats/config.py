
import os

#%%
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, 'data/sats/Val')
INPUT_DIR1 = os.path.join(DATA_DIR, 'Urban/images_png')
TARGET_DIR1 = os.path.join(DATA_DIR, 'Urban/masks_png')
INPUT_DIR2 = os.path.join(DATA_DIR, 'Rural/images_png')
TARGET_DIR2 = os.path.join(DATA_DIR, 'Rural/masks_png')
MODEL_DIR = os.path.join(DATA_DIR, 'trained_models')
MODEL_NAME = 'loveda'
IMAGE_SIZE = (256, 256)
NUM_CLASSES = 8
BATCH_SIZE = 32



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