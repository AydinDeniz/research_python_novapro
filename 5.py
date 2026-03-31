from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, load_metric
import numpy as np
import matplotlib.pyplot as plt

# Load dataset
dataset = load_dataset('glue', 'mrpc')

# Load tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Preprocess data
def preprocess_function(examples):
    return tokenizer(examples['sentence1'], examples['sentence2'], truncation=True, padding=True)

encoded_dataset = dataset.map(preprocess_function, batched=True)

# Split dataset
train_dataset = encoded_dataset['train']
eval_dataset = encoded_dataset['validation']

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Define metric
metric = load_metric('glue', 'mrpc')

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return metric.compute(predictions=predictions, references=labels)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

# Train model
trainer.train()

# Evaluate model
trainer.evaluate()

# Visualize attention weights
def visualize_attention(sentence1, sentence2, model, tokenizer):
    inputs = tokenizer(sentence1, sentence2, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)
    attentions = outputs.attentions[-1].squeeze(0).detach().numpy()

    plt.matshow(attentions)
    plt.show()

sentence1 = "This is a test sentence."
sentence2 = "This is another test sentence."
visualize_attention(sentence1, sentence2, model, tokenizer)