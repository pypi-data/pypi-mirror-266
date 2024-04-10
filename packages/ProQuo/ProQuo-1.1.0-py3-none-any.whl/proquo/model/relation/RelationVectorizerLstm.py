from collections import OrderedDict
from typing import List, Optional
from keras_preprocessing.sequence import pad_sequences
from tensorflow_text.tools.wordpiece_vocab import bert_vocab_from_dataset as bert_vocab
from tensorflow_text import BertTokenizer
import tensorflow as tf
import re


class RelationVectorizerLstm:
    max_length: int
    vocab_size: int
    tokenizer: BertTokenizer

    def __init__(self, lookup_table, max_length, lower_case):
        self.max_length = max_length
        self.vocab_size = int(lookup_table.size())
        self.tokenizer = BertTokenizer(lookup_table, lower_case=lower_case)

    @classmethod
    def from_raw(cls, fit_data, max_length, lower_case=True, vocab_save_path: Optional[str] = None):
        fit_data_mod = []

        for elem in fit_data:
            elem = re.sub(r'<REF>|<OREF>|<Q>|</Q>', '', elem, flags=re.DOTALL)
            fit_data_mod.append(elem)

        dataset = tf.data.Dataset.from_tensor_slices(fit_data_mod)

        bert_tokenizer_params = dict(lower_case=lower_case)
        reserved_tokens = ["[PAD]", "[UNK]", "<REF>", "<OREF>", "<Q>", "</Q>"]

        bert_vocab_args = dict(
            # The target vocabulary size
            vocab_size=8000,
            # Reserved tokens that must be included in the vocabulary
            reserved_tokens=reserved_tokens,
            # Arguments for `text.BertTokenizer`
            bert_tokenizer_params=bert_tokenizer_params,
            # Arguments for `wordpiece_vocab.wordpiece_tokenizer_learner_lib.learn`
            learn_params={},
        )

        vocab = bert_vocab.bert_vocab_from_dataset(
            dataset.batch(1000).prefetch(2),
            **bert_vocab_args
        )

        if vocab_save_path:
            with open(vocab_save_path, 'w', encoding='utf-8') as f:
                for token in vocab:
                    print(token, file=f)

        lookup_table = tf.lookup.StaticVocabularyTable(
            num_oov_buckets=1,
            initializer=tf.lookup.KeyValueTensorInitializer(
                keys=vocab,
                values=tf.range(len(vocab), dtype=tf.int64)))

        return cls(lookup_table, max_length, lower_case)

    @classmethod
    def from_vocab_file(cls, vocab_file_path, max_length, lower_case):
        lookup_table = tf.lookup.StaticVocabularyTable(
            num_oov_buckets=1,
            initializer=tf.lookup.TextFileInitializer(
                filename=vocab_file_path,
                key_dtype=tf.string,
                key_index=tf.lookup.TextFileIndex.WHOLE_LINE,
                value_dtype=tf.int64,
                value_index=tf.lookup.TextFileIndex.LINE_NUMBER))

        return cls(lookup_table, max_length, lower_case)

    def vectorize(self, input_list: List[str]):
        special_tokens = {'<REF>': 2, '<OREF>': 3, '<Q>': 4, '</Q>': 5}
        special_token_positions = []

        for sent in input_list:
            parts = re.split(r'(<REF>|<OREF>|<Q>|</Q>)', sent)
            pos_map = OrderedDict()
            offset = 0
            special_offset = 0
            for part in parts:
                if part in special_tokens:
                    start = offset
                    token_id = special_tokens[part]
                    pos_map[start - special_offset] = token_id
                    special_offset += len(part)

                offset += len(part)

            special_token_positions.append(pos_map)

        input_list_mod = []

        for elem in input_list:
            elem = re.sub(r'<REF>|<OREF>|<Q>|</Q>', '', elem, flags=re.DOTALL)
            input_list_mod.append(elem)

        pieces, starts, ends = self.tokenizer.tokenize_with_offsets(input_list_mod)
        pieces_merged = pieces.merge_dims(-2, -1)
        starts_merged = starts.merge_dims(-2, -1)
        ends_merged = ends.merge_dims(-2, -1)

        pieces_list = pieces_merged.to_list()
        starts_list = starts_merged.to_list()
        ends_list = ends_merged.to_list()

        for piece, starts, ends, pos_map in zip(pieces_list, starts_list, ends_list, special_token_positions):
            for token_pos, token_id in reversed(pos_map.items()):
                if token_pos <= starts[0]:
                    piece.insert(0, token_id)
                elif token_pos > ends[-1]:
                    piece.append(token_id)
                else:
                    for list_pos, end_pos in enumerate(ends):
                        if token_pos <= end_pos:
                            piece.insert(list_pos, token_id)
                            break

        sent_ints_padded = pad_sequences(pieces_list, self.max_length)
        return sent_ints_padded
