import argparse
import gensim.downloader as api
import numpy as np
import os
import shutil
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix

def download_and_read(url):
    local_file = url.split('/')[-1]
    p = tf.keras.utils.get_file(local_file, url,extract=True, cache_dir=".")
    labels, texts = [], []
    local_file = os.path.join("datasets", "SMSSpamCollection")
    
    with open(local_file, "r", encoding="utf-8") as fin:
        for line in fin:
            label, text = line.strip().split('\t')
            labels.append(1 if label == "spam" else 0)
            texts.append(text)

    return texts, labels

def build_embedding_matrix(sequences, word2idx, embedding_dim, embedding_file):
    if os.path.exists(embedding_file):
        E = np.load(embedding_file)
    else:
        vocab_size = len(word2idx)
        E = np.zeros((vocab_size, embedding_dim))
        word_vectors = api.load(EMBEDDING_MODEL)

        for word, idx in word2idx.items():
            try:
                E[idx] = word_vectors.word_vec(word)
            except KeyError:
                pass

        np.save(embedding_file, E)

    return E

class SpamClassifierModel(tf.keras.Model):
    def __init__(self, vocab_sz, embed_sz, input_length,
            num_filters, kernel_sz, output_sz, 
            run_mode, embedding_weights, 
            **kwargs):
        super(SpamClassifierModel, self).__init__(**kwargs)

        if run_mode == "scratch":
            self.embedding = tf.keras.layers.Embedding(vocab_sz, 
                embed_sz,
                input_length=input_length,
                trainable=True)

        elif run_mode == "vectorizer":
            self.embedding = tf.keras.layers.Embedding(vocab_sz, 
                embed_sz,
                input_length=input_length,
                weights=[embedding_weights],
                trainable=False)
        else:
            self.embedding = tf.keras.layers.Embedding(vocab_sz, 
                embed_sz,
                input_length=input_length,
                weights=[embedding_weights],
                trainable=True)

        self.dropout = tf.keras.layers.SpatialDropout1D(0.2)
        self.conv = tf.keras.layers.Conv1D(filters=num_filters,
            kernel_size=kernel_sz,
            activation="relu")
        self.pool = tf.keras.layers.GlobalMaxPooling1D()
        self.dense = tf.keras.layers.Dense(output_sz, 
            activation="softmax"
        )

    def call(self, x):
        x = self.embedding(x)
        x = self.dropout(x)
        x = self.conv(x)
        x = self.pool(x)
        x = self.dense(x)
        return x

DATA_DIR = "data"
EMBEDDING_NUMPY_FILE = os.path.join(DATA_DIR, "E.npy")
DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
EMBEDDING_MODEL = "glove-wiki-gigaword-300"
EMBEDDING_DIM = 300
NUM_CLASSES = 2
BATCH_SIZE = 128
NUM_EPOCHS = 3
CLASS_WEIGHTS = { 0: 1, 1: 8 }

tf.random.set_seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="run mode",
    choices=[
        "scratch",
        "vectorizer",
        "finetuning"
    ])
args = parser.parse_args()
run_mode = args.mode

texts, labels = download_and_read(DATASET_URL)

tokenizer = tf.keras.preprocessing.text.Tokenizer()

tokenizer.fit_on_texts(texts)

text_sequences = tokenizer.texts_to_sequences(texts)
text_sequences = tf.keras.preprocessing.sequence.pad_sequences(text_sequences)
num_records = len(text_sequences)
max_seqlen = len(text_sequences[0])

print("{:d} sentences, max length: {:d}".format(num_records, max_seqlen))

cat_labels = tf.keras.utils.to_categorical(labels, num_classes=NUM_CLASSES)

word2idx = tokenizer.word_index
idx2word = {v:k for k, v in word2idx.items()}
word2idx["PAD"] = 0
idx2word[0] = "PAD"
vocab_size = len(word2idx)

print("vocab size: {:d}".format(vocab_size))

dataset = tf.data.Dataset.from_tensor_slices((text_sequences, cat_labels))
dataset = dataset.shuffle(10000)
test_size = num_records // 4
val_size = (num_records - test_size) // 10
test_dataset = dataset.take(test_size)
val_dataset = dataset.skip(test_size).take(val_size)
train_dataset = dataset.skip(test_size + val_size)

test_dataset = test_dataset.batch(BATCH_SIZE, drop_remainder=True)
val_dataset = val_dataset.batch(BATCH_SIZE, drop_remainder=True)
train_dataset = train_dataset.batch(BATCH_SIZE, drop_remainder=True)

E = build_embedding_matrix(text_sequences, word2idx, EMBEDDING_DIM,
    EMBEDDING_NUMPY_FILE)

print("Embedding matrix:", E.shape)

conv_num_filters = 256
conv_kernel_size = 3
model = SpamClassifierModel(
    vocab_size, EMBEDDING_DIM, max_seqlen, 
    conv_num_filters, conv_kernel_size, NUM_CLASSES,
    run_mode, E)
model.build(input_shape=(None, max_seqlen))
model.summary()
'''
Embedding matrix: (9010, 300)
Model: "spam_classifier_model"
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
embedding (Embedding)        multiple                  2703000   
_________________________________________________________________
spatial_dropout1d (SpatialDr multiple                  0         
_________________________________________________________________
conv1d (Conv1D)              multiple                  230656    
_________________________________________________________________
global_max_pooling1d (Global multiple                  0         
_________________________________________________________________
dense (Dense)                multiple                  514       
=================================================================
Total params: 2,934,170
Trainable params: 2,934,170
Non-trainable params: 0
_________________________________________________________________
'''

model.compile(optimizer="adam", loss="categorical_crossentropy",
    metrics=["accuracy"])

model.fit(train_dataset, epochs=NUM_EPOCHS, 
    validation_data=val_dataset,
    class_weight=CLASS_WEIGHTS)

labels, predictions = [], []

for Xtest, Ytest in test_dataset:
    Ytest_ = model.predict_on_batch(Xtest)
    ytest = np.argmax(Ytest, axis=1)
    ytest_ = np.argmax(Ytest_, axis=1)
    labels.extend(ytest.tolist())
    predictions.extend(ytest.tolist())

print("test accuracy: {:.3f}".format(accuracy_score(labels, predictions)))
print("confusion matrix")
print(confusion_matrix(labels, predictions))
'''
test accuracy: 1.000
confusion matrix
[[1091    0]
 [   0  189]]
'''
'''
Epoch 1/3
29/29 [==============================] - 1s 37ms/step - loss: 0.5832 - accuracy: 0.8475 - val_loss: 0.0879 - val_accuracy: 0.9714
Epoch 2/3
29/29 [==============================] - 1s 32ms/step - loss: 0.2140 - accuracy: 0.9628 - val_loss: 0.0408 - val_accuracy: 0.9948
Epoch 3/3
29/29 [==============================] - 1s 32ms/step - loss: 0.1095 - accuracy: 0.9838 - val_loss: 0.0630 - val_accuracy: 0.9818
'''