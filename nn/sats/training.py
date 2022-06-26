"""
Code adjusted from F.Cholet: https://keras.io/examples/vision/oxford_pets_image_segmentation/
"""


#%%
import random
from PIL.ImageOps import autocontrast
import numpy as np
import tensorflow as tf
from tensorflow import keras

from helpers import displayColorImage, displaySegmentData, displaySegmentImage, saveModel
from config import input_img_paths, target_img_paths, BATCH_SIZE, IMAGE_SIZE, NUM_CLASSES, MODEL_NAME, MODEL_DIR
from loader import SegmentationDataLoader
from net import unet





#%%

for input_path, target_path in zip(input_img_paths[:10], target_img_paths[:10]):
    print(input_path, "|", target_path)



imgNr = 600
displayColorImage(input_img_paths[imgNr])
displaySegmentImage(target_img_paths[imgNr])



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

# Free up RAM in case the model definition cells were run multiple times
keras.backend.clear_session()
# Build model
model = unet(IMAGE_SIZE, NUM_CLASSES)
# We use the "sparse" version of categorical_crossentropy because our target data is integers.
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy")

callbacks = [keras.callbacks.ModelCheckpoint(f"{MODEL_DIR}/{MODEL_NAME}_checkpoint.h5", save_best_only=True)]

# Train the model, doing validation at the end of each epoch.
epochs = 15
model.fit(train_gen, epochs=epochs, validation_data=val_gen, callbacks=callbacks)

saveModel(model, MODEL_DIR, MODEL_NAME)


#%%
# Generate predictions for all images in the validation set

val_gen = SegmentationDataLoader(BATCH_SIZE, IMAGE_SIZE, val_input_img_paths, val_target_img_paths)
val_preds = model.predict(val_gen)

# Display results for validation image #10
i = 37
# Display input image
displayColorImage(val_input_img_paths[i])
# Display ground-truth target mask
displaySegmentImage(val_target_img_paths[i])
# Display mask predicted by our model
displaySegmentData(val_preds[i])  # Note that the model only sees inputs at 150x150.

# %%
