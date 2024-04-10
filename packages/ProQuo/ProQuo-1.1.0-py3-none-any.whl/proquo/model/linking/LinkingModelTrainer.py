import numpy as np

import tensorflow as tf
from tensorflow.keras.utils import Sequence
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers.legacy import Adam

import transformers
from os.path import join
import torch


class DataGenerator(Sequence):

    def __init__(self, examples, labels, batch_size, vectorizer):
        self.examples = examples
        self.labels = labels
        self.batch_size = batch_size
        self.vectorizer = vectorizer

    def __len__(self):
        return (np.ceil(len(self.examples) / self.batch_size)).astype(np.int32)

    def __getitem__(self, idx):
        batch_x_ex = self.examples[idx * self.batch_size: (idx + 1) * self.batch_size]
        input_ids, attention_masks, token_type_ids = self.vectorizer.vectorize(batch_x_ex)
        batch_y = self.labels[idx * self.batch_size: (idx + 1) * self.batch_size]
        labels = np.array(batch_y, dtype="int32")
        return [input_ids, attention_masks, token_type_ids], labels


# TODO: merge with TrainLinking.py?
def train_model(vectorizer, model_name, batch_size, num_epochs, train_examples, train_labels, val_examples,
                val_labels, output_folder_path):
    model = transformers.TFBertForSequenceClassification.from_pretrained(model_name, num_labels=2, from_pt=True)
    model.resize_token_embeddings(vectorizer.vocab_size)

    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(loss=loss, optimizer=Adam(0.00001), metrics=['accuracy'])
    print(model.summary())

    checkpoint_model_path = join(output_folder_path, f'checkpoint.h5')
    model_checkpoint = ModelCheckpoint(checkpoint_model_path, monitor='val_loss', mode='min', save_best_only=True,
                                       save_weights_only=True)

    training_generator = DataGenerator(train_examples, train_labels, batch_size, vectorizer)
    validation_generator = DataGenerator(val_examples, val_labels, batch_size, vectorizer)

    model.fit(x=training_generator,
              steps_per_epoch=int(len(train_examples) // batch_size),
              epochs=num_epochs,
              validation_data=validation_generator,
              validation_steps=int(len(val_examples) // batch_size),
              callbacks=[model_checkpoint])

    model.load_weights(checkpoint_model_path)
    best_model_path = join(output_folder_path, 'model')
    model.save_pretrained(best_model_path)
