from typing import List, Tuple
import transformers
import tensorflow as tf

transformers.logging.set_verbosity_error()


class LinkingVectorizer:
    max_length: int
    vocab_size: int
    tokenizer: transformers.BertTokenizer

    def __init__(self, max_length, tokenizer):
        self.max_length = max_length
        self.tokenizer = tokenizer
        self.vocab_size = len(self.tokenizer)

    @classmethod
    def from_raw(cls, model_name, max_length, lower_case):
        tokenizer = transformers.BertTokenizer.from_pretrained(
            model_name, do_lower_case=lower_case
        )

        special_tokens_dict = {'additional_special_tokens': ['<S>', '</S>', '<T>', '</T>']}
        tokenizer.add_special_tokens(special_tokens_dict)
        return cls(max_length, tokenizer)

    @classmethod
    def from_saved(cls, max_length, tokenizer_path, lower_case):
        tokenizer = transformers.BertTokenizer.from_pretrained(
            tokenizer_path, do_lower_case=lower_case
        )

        return cls(max_length, tokenizer)

    def vectorize(self, input_list: List[Tuple[str, str]]):
        encoded = self.tokenizer.batch_encode_plus(
            input_list,
            truncation=True,
            add_special_tokens=True,
            max_length=self.max_length,
            return_attention_mask=True,
            return_token_type_ids=True,
            padding='max_length',
            return_tensors="tf",
        )

        # Convert batch of encoded features to numpy array.
        input_ids = tf.constant(encoded["input_ids"], dtype="int32")
        attention_masks = tf.constant(encoded["attention_mask"], dtype="int32")
        token_type_ids = tf.constant(encoded["token_type_ids"], dtype="int32")

        return input_ids, attention_masks, token_type_ids
