"""
Code adjusted from F.Cholet: https://keras.io/examples/vision/oxford_pets_image_segmentation/
"""


#%%
import os
import random
import PIL
import numpy as np
from tensorflow import keras

from helpers import displayColorImage, displaySegmentImage, saveModel
from loader import OxfordPets
from net import unet




#%%

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, 'data/pets')
INPUT_DIR = os.path.join(DATA_DIR, "images/")
TARGET_DIR = os.path.join(DATA_DIR, 'annotations/trimaps/')
MODEL_DIR = os.path.join(DATA_DIR, 'trained_models')
MODEL_NAME = 'Oxford'
IMAGE_SIZE = (160, 160)
NUM_CLASSES = 3
BATCH_SIZE = 32



#%%
input_img_paths = sorted([
        os.path.join(INPUT_DIR, fname)
            for fname in os.listdir(INPUT_DIR) if fname.endswith(".jpg")
])

target_img_paths = sorted([
        os.path.join(TARGET_DIR, fname)
            for fname in os.listdir(TARGET_DIR) if fname.endswith(".png") and not fname.startswith(".")
])

print("Number of samples:", len(input_img_paths))

for input_path, target_path in zip(input_img_paths[:10], target_img_paths[:10]):
    print(input_path, "|", target_path)


#%%
imgNr = 9
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
train_gen = OxfordPets(BATCH_SIZE, IMAGE_SIZE, train_input_img_paths, train_target_img_paths)
val_gen   = OxfordPets(BATCH_SIZE, IMAGE_SIZE, val_input_img_paths, val_target_img_paths)


#%%

# Free up RAM in case the model definition cells were run multiple times
keras.backend.clear_session()
# Build model
model = unet(IMAGE_SIZE, NUM_CLASSES)
model.summary()
# Configure the model for training.
# We use the "sparse" version of categorical_crossentropy because our target data is integers.
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy")

callbacks = [keras.callbacks.ModelCheckpoint(f"{MODEL_DIR}/{MODEL_NAME}_checkpoint.h5", save_best_only=True)]

# Train the model, doing validation at the end of each epoch.
epochs = 15
model.fit(train_gen, epochs=epochs, validation_data=val_gen, callbacks=callbacks)

saveModel(model, MODEL_DIR, MODEL_NAME)


#%%
# Generate predictions for all images in the validation set

val_gen = OxfordPets(BATCH_SIZE, IMAGE_SIZE, val_input_img_paths, val_target_img_paths)
val_preds = model.predict(val_gen)


from IPython.display import Image, display
def display_mask(i):
    """Quick utility to display a model's prediction."""
    mask = np.argmax(val_preds[i], axis=-1)
    mask = np.expand_dims(mask, axis=-1)
    img = PIL.ImageOps.autocontrast(keras.preprocessing.image.array_to_img(mask))
    display(img)


# Display results for validation image #10
i = 10
# Display input image
displayColorImage(val_input_img_paths[i])
# Display ground-truth target mask
displaySegmentImage(val_target_img_paths[i])
# Display mask predicted by our model
display_mask(i)  # Note that the model only sees inputs at 150x150.
