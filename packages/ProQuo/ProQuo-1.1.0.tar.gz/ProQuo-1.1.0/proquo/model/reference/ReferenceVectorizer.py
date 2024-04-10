from typing import List
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer


class ReferenceVectorizer:

    tokenizer: Tokenizer
    max_length: int
    max_id: int
    lower_case: bool

    def __init__(self, tokenizer, max_length, lower_case):
        self.lower_case = lower_case
        self.tokenizer = tokenizer
        self.max_id = len(self.tokenizer.word_index)
        self.max_length = max_length

    @classmethod
    def from_raw(cls, fit_data, max_length, lower_case=True):
        if lower_case:
            fit_data = [x.lower() for x in fit_data]

        tokenizer = Tokenizer(char_level=True)
        tokenizer.fit_on_texts(fit_data)
        return cls(tokenizer, max_length, lower_case)

    @classmethod
    def from_vocab_file(cls, vocab_file_path, max_length, lower_case):
        word_index = {}

        with open(vocab_file_path, 'r', encoding='utf-8') as vocab_file:
            for count, line in enumerate(vocab_file):
                word_index[line.rstrip('\n')] = count + 1

        tokenizer = Tokenizer(char_level=True)
        tokenizer.word_index = word_index
        return cls(tokenizer, max_length, lower_case)

    def vectorize(self, input_list: List[str]):
        if self.lower_case:
            input_list = [x.lower() for x in input_list]

        input_sequences = self.tokenizer.texts_to_sequences(input_list)
        input_sequences_padded = pad_sequences(input_sequences, maxlen=self.max_length)
        return input_sequences_padded
