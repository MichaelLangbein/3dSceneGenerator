#%% 
# 
# https://huggingface.co/docs/transformers/v4.20.1/en/task_summary
# https://huggingface.co/tasks/object-detection
# 
# from transformers import pipeline
# model = pipeline("object-detection")
# imagePath = "./data/craiyon_2022-6-26_20-43-13.png"
# model(imagePath)




#%%
# from transformers import TrainingArguments, Trainer, pipeline
# import numpy as np
# from datasets import load_metric, load_dataset

# model = from_pretrained('segformer-b0-finetuned-ade-512-512')


# dataset = load_dataset("scene_parse_150")
# small_train_dataset = dataset["train"].shuffle(seed=42).select(range(1000))
# small_eval_dataset = dataset["test"].shuffle(seed=42).select(range(1000))


# training_args = TrainingArguments(output_dir="test_trainer", evaluation_strategy="epoch")
# metric = load_metric("accuracy")

# def compute_metrics(eval_pred):
#     logits, labels = eval_pred
#     predictions = np.argmax(logits, axis=-1)
#     return metric.compute(predictions=predictions, references=labels)


# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=small_train_dataset,
#     eval_dataset=small_eval_dataset,
#     compute_metrics=compute_metrics,
# )

# trainer.train()
# %%
from transformers import SegformerFeatureExtractor, SegformerForSemanticSegmentation
from PIL import Image
import requests

feature_extractor = SegformerFeatureExtractor.from_pretrained("nvidia/segformer-b0-finetuned-ade-512-512")
model = SegformerForSemanticSegmentation.from_pretrained("nvidia/segformer-b0-finetuned-ade-512-512")

url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)

inputs = feature_extractor(images=image, return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits  # shape (batch_size, num_labels, height/4, width/4)

# %%
