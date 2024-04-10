from tensorflow.keras.utils import Sequence
from tensorflow.keras.layers import Dense, Input, LSTM, Bidirectional, Lambda, Embedding
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers.legacy import Adam
import numpy as np
from os.path import join


from proquo.model.reference.ReferenceVectorizer import ReferenceVectorizer


class DataGenerator(Sequence):

    def __init__(self, data_1, data_2, labels, batch_size):
        self.data_1 = data_1
        self.data_2 = data_2
        self.labels = labels
        self.batch_size = batch_size

    def __len__(self):
        return (np.ceil(len(self.data_1) / self.batch_size)).astype(np.int32)

    def __getitem__(self, idx):
        batch_x_1 = self.data_1[idx * self.batch_size: (idx + 1) * self.batch_size]
        batch_x_2 = self.data_2[idx * self.batch_size: (idx + 1) * self.batch_size]
        batch_y = self.labels[idx * self.batch_size: (idx + 1) * self.batch_size]
        return [batch_x_1, batch_x_2], batch_y


class ReferenceModelTrainer:
    def __init__(self, max_sequence_length, lower_case, num_dense_units, num_lstm_units, dropout_rate, batch_size,
                 num_epochs):
        self.max_sequence_length = max_sequence_length
        self.lower_case = lower_case
        self.num_dense_units = num_dense_units
        self.num_lstm_units = num_lstm_units
        self.dropout_rate = dropout_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs

    def get_model(self, max_id):
        model_input_1 = Input(shape=(self.max_sequence_length,))
        model_input_2 = Input(shape=(self.max_sequence_length,))

        embedding_layer = Embedding(input_dim=max_id + 1, output_dim=self.num_dense_units,
                                    input_length=self.max_sequence_length, mask_zero=True)

        embedding_1 = embedding_layer(model_input_1)
        embedding_2 = embedding_layer(model_input_2)

        lstm = Bidirectional(LSTM(self.num_lstm_units, return_sequences=False, dropout=self.dropout_rate))

        x1 = lstm(embedding_1)
        x2 = lstm(embedding_2)

        l1_norm = lambda x: 1 - abs(x[0] - x[1])
        merged = Lambda(function=l1_norm, output_shape=lambda x: x[0], name='L1_distance')([x1, x2])
        preds = Dense(1, activation='sigmoid')(merged)
        model = Model(inputs=[model_input_1, model_input_2], outputs=preds)

        return model

    def train_model(self, train_word_pairs, train_labels, val_word_pairs, val_labels, output_dir):
        single_list = []

        for wp in train_word_pairs:
            single_list.append(wp[0])
            single_list.append(wp[1])

        vectorizer = ReferenceVectorizer.from_raw(single_list, self.max_sequence_length, self.lower_case)

        vocab = ''
        for key, value in vectorizer.tokenizer.word_index.items():
            if value == 1:
                vocab += key
            else:
                vocab += f'\n{key}'

        vocab_path = join(output_dir, 'vocab.txt')
        with open(vocab_path, "w", encoding='utf-8') as vocab_file:
            vocab_file.write(vocab)

        train_sentences_1 = [x[0] for x in train_word_pairs]
        train_sentences_2 = [x[1] for x in train_word_pairs]
        val_sentences_1 = [x[0] for x in val_word_pairs]
        val_sentences_2 = [x[1] for x in val_word_pairs]

        train_data_x_1 = vectorizer.vectorize(train_sentences_1)
        train_data_x_2 = vectorizer.vectorize(train_sentences_2)
        val_data_x_1 = vectorizer.vectorize(val_sentences_1)
        val_data_x_2 = vectorizer.vectorize(val_sentences_2)

        train_labels = np.asarray(train_labels).astype(np.float16).reshape((-1, 1))
        val_labels = np.asarray(val_labels).astype(np.float16).reshape((-1, 1))

        model = self.get_model(vectorizer.max_id)
        model.compile(loss='binary_crossentropy', optimizer=Adam(0.001), metrics=['acc'])

        early_stopping = EarlyStopping(monitor='val_loss', patience=3)
        name = f'lstm_{self.num_lstm_units}_{self.dropout_rate}'

        best_model_path = join(output_dir, name + '.h5')
        model_checkpoint = ModelCheckpoint(best_model_path, save_best_only=True, save_weights_only=False)

        print(model.summary())

        training_generator = DataGenerator(train_data_x_1, train_data_x_2, train_labels, self.batch_size)
        validation_generator = DataGenerator(val_data_x_1, val_data_x_2, val_labels, self.batch_size)

        model.fit(x=training_generator,
                  steps_per_epoch=int(len(train_data_x_1) // self.batch_size),
                  epochs=self.num_epochs,
                  validation_data=validation_generator,
                  validation_steps=int(len(val_data_x_1) // self.batch_size),
                  callbacks=[early_stopping, model_checkpoint])
