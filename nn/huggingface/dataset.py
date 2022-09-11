#%%

# https://huggingface.co/docs/datasets/master/en/dataset_script

#%% For comparison: a existing dataset.

from datasets import load_dataset
dataset = load_dataset("scene_parse_150")
