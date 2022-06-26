#%%
from tensorflow import keras
from loader import SegmentationDataLoader
from config import BATCH_SIZE, IMAGE_SIZE, input_img_paths, target_img_paths
from helpers import displayColorImage, displaySegmentData, displaySegmentImage


#%%
path = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/data/trained_models/loveda_24/06/2022_16:04:24"
model = keras.models.load_model(path)

# %%
nr_samples = 100
val_input_img_paths = input_img_paths[-nr_samples:]
val_target_img_paths = target_img_paths[-nr_samples:]

#%%
val_gen = SegmentationDataLoader(BATCH_SIZE, IMAGE_SIZE, val_input_img_paths, val_target_img_paths)

val_preds = model.predict(val_gen)

# Display results for validation image #10
i = 17
# Display input image
displayColorImage(val_input_img_paths[i])
# Display ground-truth target mask
displaySegmentImage(val_target_img_paths[i])
# Display prediction
displaySegmentData(val_preds[i])


#%%


# %%
import tensorflowjs as tfjs

targetPath = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/trained_models/tfjs/"
tfjs.converters.save_keras_model(model, targetPath)
targetPath2 = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/trained_models/tfjs2/"
tfjs.converters.convert_tf_saved_model(targetPath, targetPath2)

# %%
