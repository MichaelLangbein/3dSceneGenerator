#%%
from tensorflow import keras
from config import BATCH_SIZE, IMAGE_SIZE, input_img_paths, target_img_paths
from loader import SegmentationDataLoader
from helpers import displayColorImage, displaySegmentImage


#%%
path = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/data/sats/Val/trained_models/loveda_24/06/2022_16:04:24"
model = keras.models.load_model(path)

# %%
nr_samples = 100
val_input_img_paths = input_img_paths[-nr_samples:]
val_target_img_paths = target_img_paths[-nr_samples:]

# %%
val_gen = SegmentationDataLoader(BATCH_SIZE, IMAGE_SIZE, val_input_img_paths, val_target_img_paths)

val_preds = model.predict(val_gen)

# Display results for validation image #10
i = 17
# Display input image
displayColorImage(val_input_img_paths[i])
# Display ground-truth target mask
displaySegmentImage(val_target_img_paths[i])


# %%
import tensorflowjs as tfjs

targetPath = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/data/tfjs/"
tfjs.converters.save_keras_model(model, targetPath)

# %%
