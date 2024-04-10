import numpy as np

from tensorflow.keras.utils import Sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Embedding
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from os.path import join

from proquo.model.relation.RelationVectorizerLstm import RelationVectorizerLstm
import tensorflow as tf


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
        batch_x = self.vectorizer.vectorize(batch_x_ex)
        batch_y = self.labels[idx * self.batch_size: (idx + 1) * self.batch_size]
        return batch_x, batch_y


class RelationModelLstmTrainer:

    def __init__(self, max_sequence_length, lower_case, num_dense_units, num_lstm_units, dropout_rate,
                 batch_size, num_epochs):
        self.max_sequence_length = max_sequence_length
        self.lower_case = lower_case
        self.num_lstm_units = num_lstm_units
        self.num_dense_units = num_dense_units
        self.dropout_rate = dropout_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs

    def get_model(self, vocab_size):
        model = Sequential()

        model.add(Embedding(input_dim=vocab_size, output_dim=self.num_dense_units,
                            input_length=self.max_sequence_length, mask_zero=True))
        model.add(Dropout(self.dropout_rate))
        model.add(Bidirectional(LSTM(self.num_lstm_units, dropout=self.dropout_rate, return_sequences=False)))
        model.add(Dropout(self.dropout_rate))
        model.add(Dense(1, activation='sigmoid'))

        return model

    def train_model(self, train_examples, train_labels, val_examples, val_labels, output_dir):
        vocab_path = join(output_dir, 'vocab.txt')
        vectorizer = RelationVectorizerLstm.from_raw(train_examples, self.max_sequence_length, self.lower_case,
                                                     vocab_save_path=vocab_path)

        train_labels = np.asarray(train_labels).astype(np.float16).reshape((-1, 1))
        val_labels = np.asarray(val_labels).astype(np.float16).reshape((-1, 1))

        model = self.get_model(vectorizer.vocab_size)

        model.compile(loss='binary_crossentropy', optimizer=Adam(0.01), metrics=['accuracy'])

        early_stopping = EarlyStopping(monitor='val_loss', patience=3)
        name = f'lstm_{self.num_lstm_units}_{self.dropout_rate}'

        best_model_path = join(output_dir, name + '.h5')
        model_checkpoint = ModelCheckpoint(best_model_path, monitor='val_loss', mode='min', save_best_only=True,
                                           save_weights_only=False)

        print(model.summary())

        training_generator = DataGenerator(train_examples, train_labels, self.batch_size, vectorizer)
        validation_generator = DataGenerator(val_examples, val_labels, self.batch_size, vectorizer)

        model.fit(x=training_generator,
                  steps_per_epoch=int(len(train_examples) // self.batch_size),
                  epochs=self.num_epochs,
                  validation_data=validation_generator,
                  validation_steps=int(len(val_examples) // self.batch_size),
                  callbacks=[early_stopping, model_checkpoint],
                  workers=1, use_multiprocessing=False, max_queue_size=10, shuffle=True)
