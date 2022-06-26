#%%
import os
import image_slicer as isl

# %%

dataDir = './data/Train'
for dirPath, dirNames, fileNames in os.walk(dataDir):
    for fileName in fileNames:
        isl.slice(os.path.join(dirPath, fileName), 4)
# %%
