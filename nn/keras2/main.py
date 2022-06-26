#%%
import os
import numpy as np
import tensorflow as tf
import tensorflow.keras as tfk
from tensorflow.keras.preprocessing.image import load_img, array_to_img
from PIL.ImageOps import autocontrast
from IPython.display import Image, display


# %%
IMAGE_SIZE = 256
BATCH_SIZE = 4
NUM_CLASSES = 7
DATA_DIR = "./data/Train"
NUM_TRAIN_IMAGES = 1000
NUM_VAL_IMAGES = 50


#%%
images = []
masks = []
for dirPath, dirNames, fileNames in os.walk(DATA_DIR):
    for fileName in fileNames:
        if '_' in fileName:
            if 'images_png' in dirPath:
                images.append(os.path.join(dirPath, fileName))
            elif 'masks_png' in dirPath:
                masks.append(os.path.join(dirPath, fileName))

trainImages = images[:NUM_TRAIN_IMAGES]
trainMasks  = masks[:NUM_TRAIN_IMAGES]
valImages   = images[NUM_TRAIN_IMAGES : NUM_TRAIN_IMAGES + NUM_VAL_IMAGES]
valMasks    = masks[NUM_TRAIN_IMAGES : NUM_TRAIN_IMAGES + NUM_VAL_IMAGES]


def readMask(imagePath):
    image = tf.io.read_file(imagePath)
    image = tf.image.decode_png(image, channels=1)
    image.set_shape([None, None, 1])
    image = tf.image.resize(images=image, size=[IMAGE_SIZE, IMAGE_SIZE])
    return image


def readImage(imagePath):
    image = tf.io.read_file(imagePath)
    image = tf.image.decode_png(image, channels=3)
    image.set_shape([None, None, 3])
    image = tf.image.resize(images=image, size=[IMAGE_SIZE, IMAGE_SIZE])
    # image = image / 127.5 - 1
    return image


def loadData(imagePath, maskPath):
    image = readImage(imagePath)
    mask = readMask(maskPath)
    return image, mask


def dataGenerator(imageList, maskList):
    dataset = tf.data.Dataset.from_tensor_slices((imageList, maskList))
    dataset = dataset.map(loadData, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
    return dataset


train_dataset = dataGenerator(trainImages, trainMasks)
val_dataset = dataGenerator(valImages, valMasks)

print("Train Dataset:", train_dataset)
print("Val Dataset:", val_dataset)





# %%
def convolution_block(
    block_input,
    num_filters=256,
    kernel_size=3,
    dilation_rate=1,
    padding="same",
    use_bias=False,
):
    x = tfk.layers.Conv2D(
        num_filters,
        kernel_size=kernel_size,
        dilation_rate=dilation_rate,
        padding="same",
        use_bias=use_bias,
        kernel_initializer=tfk.initializers.HeNormal(),
    )(block_input)
    x = tfk.layers.BatchNormalization()(x)
    return tf.nn.relu(x)


def DilatedSpatialPyramidPooling(dspp_input):
    dims = dspp_input.shape
    x = tfk.layers.AveragePooling2D(pool_size=(dims[-3], dims[-2]))(dspp_input)
    x = convolution_block(x, kernel_size=1, use_bias=True)
    out_pool = tfk.layers.UpSampling2D(
        size=(dims[-3] // x.shape[1], dims[-2] // x.shape[2]), interpolation="bilinear",
    )(x)

    out_1 = convolution_block(dspp_input, kernel_size=1, dilation_rate=1)
    out_6 = convolution_block(dspp_input, kernel_size=3, dilation_rate=6)
    out_12 = convolution_block(dspp_input, kernel_size=3, dilation_rate=12)
    out_18 = convolution_block(dspp_input, kernel_size=3, dilation_rate=18)

    x = tfk.layers.Concatenate(axis=-1)([out_pool, out_1, out_6, out_12, out_18])
    output = convolution_block(x, kernel_size=1)
    return output


def DeeplabV3Plus(image_size, num_classes):
    model_input = tfk.Input(shape=(image_size, image_size, 3))
    resnet50 = tfk.applications.ResNet50(
        weights="imagenet", include_top=False, input_tensor=model_input
    )
    x = resnet50.get_layer("conv4_block6_2_relu").output
    x = DilatedSpatialPyramidPooling(x)

    input_a = tfk.layers.UpSampling2D(
        size=(image_size // 4 // x.shape[1], image_size // 4 // x.shape[2]),
        interpolation="bilinear",
    )(x)
    input_b = resnet50.get_layer("conv2_block3_2_relu").output
    input_b = convolution_block(input_b, num_filters=48, kernel_size=1)

    x = tfk.layers.Concatenate(axis=-1)([input_a, input_b])
    x = convolution_block(x)
    x = convolution_block(x)
    x = tfk.layers.UpSampling2D(
        size=(image_size // x.shape[1], image_size // x.shape[2]),
        interpolation="bilinear",
    )(x)
    model_output = tfk.layers.Conv2D(num_classes, kernel_size=(1, 1), padding="same")(x)
    return tfk.Model(inputs=model_input, outputs=model_output)


model = DeeplabV3Plus(image_size=IMAGE_SIZE, num_classes=NUM_CLASSES)
model.summary()



# %%
tfk.backend.clear_session()
model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
history = model.fit(train_dataset, validation_data=val_dataset, epochs=25)


#%%




#%%
import matplotlib.pyplot as plt 

plt.plot(history.history["loss"])
plt.title("Training Loss")
plt.ylabel("loss")
plt.xlabel("epoch")
plt.show()

plt.plot(history.history["accuracy"])
plt.title("Training Accuracy")
plt.ylabel("accuracy")
plt.xlabel("epoch")
plt.show()

plt.plot(history.history["val_loss"])
plt.title("Validation Loss")
plt.ylabel("val_loss")
plt.xlabel("epoch")
plt.show()

plt.plot(history.history["val_accuracy"])
plt.title("Validation Accuracy")
plt.ylabel("val_accuracy")
plt.xlabel("epoch")
plt.show()



#%%




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


valPreds = model.predict(val_dataset)

# Display results for validation image #10
i = 21
# Display input image
displayColorImage(valImages[i])
# Display ground-truth target mask
displaySegmentImage(valMasks[i])
# Display prediction
displaySegmentData(valPreds[i])



# %%
import tensorflowjs as tfjs

targetPath = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/trained_models/tfjs/"
tfjs.converters.save_keras_model(model, targetPath)
targetPath2 = "/home/michael/Desktop/code/3dSceneGenerator/nn/sats/trained_models/tfjs2/"
tfjs.converters.convert_tf_saved_model(targetPath, targetPath2)

# %%