import numpy as np

import tensorflow as tf
from tensorflow.keras.utils import Sequence
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers.legacy import Adam

import transformers
from os.path import join


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


class RelationModelBertTrainer:

    def __init__(self, vectorizer, batch_size, num_epochs):
        self.vectorizer = vectorizer
        self.batch_size = batch_size
        self.num_epochs = num_epochs

    def get_model(self):
        model = transformers.TFBertForSequenceClassification.from_pretrained('bert-base-german-dbmdz-uncased',
                                                                             num_labels=2, from_pt=True)
        model.resize_token_embeddings(self.vectorizer.vocab_size)

        return model

    def train_model(self, train_examples, train_labels, val_examples, val_labels, output_dir):
        model = self.get_model()

        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        model.compile(loss=loss, optimizer=Adam(0.00001), metrics=['accuracy'])
        print(model.summary())

        early_stopping = EarlyStopping(monitor='val_loss', patience=3)

        checkpoint_model_path = join(output_dir, f'bert.h5')
        model_checkpoint = ModelCheckpoint(checkpoint_model_path, monitor='val_loss', mode='min', save_best_only=True,
                                           save_weights_only=True)

        training_generator = DataGenerator(train_examples, train_labels, self.batch_size, self.vectorizer)
        validation_generator = DataGenerator(val_examples, val_labels, self.batch_size, self.vectorizer)

        model.fit(x=training_generator,
                  steps_per_epoch=int(len(train_examples) // self.batch_size),
                  epochs=self.num_epochs,
                  validation_data=validation_generator,
                  validation_steps=int(len(val_examples) // self.batch_size),
                  callbacks=[early_stopping, model_checkpoint])

        model.load_weights(checkpoint_model_path)
        best_model_path = join(output_dir, 'bert')
        model.save_pretrained(best_model_path)
