import re
from typing import List, Tuple
from quid.match.Match import Match
from quid.match.MatchSpan import MatchSpan

from proquo.core import Helper
from proquo.core.Quote import Quote
import tensorflow as tf

from proquo.model.linking.LinkingVectorizer import LinkingVectorizer
from transformers.modeling_tf_utils import TFPreTrainedModel

import logging

from kpcommons import Util, Footnote


# noinspection PyMethodMayBeStatic
class ProQuoLm:
    # TODO: Make these customizable
    SCORE_CUTOFF: int = 0.85
    WITHOUT_REF_SEARCH_RADIUS = 500
    SOURCE_PARALLEL_LAST_PAGE = 63
    LONG_MIN_LENGTH = 5
    LINKING_MAX_LENGTH = 200
    BERT_LINK_MIN_PROB: float = 0.5

    def __init__(self, linking_model: TFPreTrainedModel, linking_vectorizer: LinkingVectorizer, open_quote: str = None,
                 close_quote: str = None):
        """
        :param linking_model: The model
        :param linking_vectorizer: The vectorizer to use to tokenize and encode inputs
        :param open_quote: Character used for opening quotation marks
        :param close_quote: Character used for closing quotation marks
        """
        self.source_cache = {}
        self.hashes = None
        self.source_text_parallel_print = False
        self.linking_model = linking_model
        self.linking_vectorizer = linking_vectorizer
        self.open_quote = open_quote
        self.close_quote = close_quote

    def compare(self, source_text: str, target_text: str, quid_matches: List[Match]) -> List[Match]:
        """
        Compare the two input texts and return a list of matching sequences.
        :param source_text: A source text
        :param target_text: A target text
        :param quid_matches: A list of matches from Quid to be used as candidates for short matches
        :return: A list of found matches
        """
        source_text_cleaned = Helper.clean_text(source_text)
        source_text_hash = hash(source_text_cleaned)
        if source_text_hash in self.source_cache:
            self.hashes = self.source_cache[source_text_hash]
        else:
            self.hashes = Helper.init_lsh_hashes(source_text_cleaned)
            self.source_cache[source_text_hash] = self.hashes

        short_matches: List[Match] = Helper.filter_short_matches(source_text_cleaned, target_text, quid_matches,
                                                                 self.LONG_MIN_LENGTH)

        all_quotes: List[Quote] = Helper.get_quotations(target_text, self.LONG_MIN_LENGTH, self.open_quote,
                                                        self.close_quote)
        footnote_ranges: List[Tuple[int, int]] = Footnote.get_footnote_ranges_without_offset(target_text)

        main_quotes: List[Quote] = []

        for q in all_quotes:
            if not Footnote.is_range_in_ranges(q.start, q.end, footnote_ranges):
                main_quotes.append(q)

        result_matches_bert: List[Match] = self.__predict_links(main_quotes, short_matches, source_text,
                                                                source_text_cleaned, target_text)
        return result_matches_bert

    def __predict_links(self, short_quotes: List[Quote], short_matches: List[Match], source_text: str,
                        source_text_cleaned: str, target_text: str) -> List[Match]:
        """
        Takes a list of short quotes and tries to find matches in the source text.
        :param short_quotes: A list of short quotes
        :param short_matches: A list of short matches from Quid
        :param source_text: The source text
        :param target_text: The target text
        :return: A list of matches, i.e. the short quotes for which a match in the source text could be determined.
        """

        result: List[Match] = []

        for sq in short_quotes:
            if not re.search(r'\w', sq.text):
                logging.warning(f'Quote "{sq.text}" does not contain any characters!')
                continue

            match_len = len(sq.text.split())

            if match_len == 1:
                candidates = self.__search_single_word(sq, source_text_cleaned)
            else:
                candidates = self.__search_multi_word(short_matches, sq, source_text_cleaned)

            if len(candidates) == 0:
                continue

            combinations = []

            for c in candidates:
                le_source_text, le_target_text = self.__prepare_link_texts(sq, c, source_text_cleaned, target_text)
                combinations.append((le_source_text, le_target_text))

            preds = self.__predict_link(combinations)

            best_candidate = None
            best_pred = 0

            for c, pred in zip(candidates, preds):
                if pred > self.BERT_LINK_MIN_PROB:
                    if pred > best_pred:
                        best_pred = pred
                        best_candidate = c

            if best_candidate:
                quote_source_text = source_text[best_candidate[0]:best_candidate[1]]
                source_span = MatchSpan(best_candidate[0], best_candidate[1], quote_source_text)
                target_span = MatchSpan(sq.start, sq.end, sq.text)
                match = Match(source_span, target_span)
                result.append(match)

        return result

    def __prepare_link_texts(self, sq: Quote, candidate: Tuple[int, int], source_text: str, target_text: str)\
            -> Tuple[str, str]:
        """
        Prepare passages from the source and target text to be used in the linking model to determine the best match
        for a quotation.
        :param sq: A quote
        :param candidate: A list of start and end positions of candidates in the source text
        :param source_text: The source text
        :param target_text: The target text
        :return: The prepared source and target text passages
        """

        source_start = candidate[0]
        source_end = candidate[1]
        target_start = sq.start
        target_end = sq.end

        source_quote_text = source_text[source_start:source_end].replace('\n', ' ')
        source_quote_length = len(source_quote_text.split())
        source_rest_len = self.LINKING_MAX_LENGTH - source_quote_length

        target_quote_text = target_text[target_start:target_end].replace('\n', ' ')
        target_quote_length = len(target_quote_text.split())
        target_rest_len = self.LINKING_MAX_LENGTH - target_quote_length

        if source_rest_len <= 0 or target_rest_len <= 0:
            return '', ''

        source_text_before = source_text[:source_start]
        source_text_after = source_text[source_end:]

        source_text_before = re.sub(r'\[\[\[((?:.|\n)+?)]]]', ' ', source_text_before)
        source_text_after = re.sub(r'\[\[\[((?:.|\n)+?)]]]', ' ', source_text_after)

        target_text_before = target_text[:target_start]
        target_text_after = target_text[target_end:]

        target_text_before = re.sub(r'\[\[\[((?:.|\n)+?)]]]', ' ', target_text_before)
        target_text_after = re.sub(r'\[\[\[((?:.|\n)+?)]]]', ' ', target_text_after)

        # TODO: check if is in footnote?

        source_parts_before = source_text_before.split()
        source_parts_after = source_text_after.split()

        source_parts_before_count = len(source_parts_before)
        source_parts_after_count = len(source_parts_after)

        source_count_before = min(round(source_rest_len / 2), source_parts_before_count)
        source_count_after = min(source_rest_len - source_count_before, source_parts_after_count)

        source_text_before = ' '.join(source_parts_before[-source_count_before:])
        source_text_after = ' '.join(source_parts_after[:source_count_after])

        le_source_text = f'{source_text_before} <S> {source_quote_text} </S> {source_text_after}'

        target_parts_before = target_text_before.split()
        target_parts_after = target_text_after.split()

        target_parts_before_count = len(target_parts_before)
        target_parts_after_count = len(target_parts_after)

        target_count_before = min(round(target_rest_len / 2), target_parts_before_count)
        target_count_after = min(target_rest_len - target_count_before, target_parts_after_count)

        target_text_before = ' '.join(target_parts_before[-target_count_before:])
        target_text_after = ' '.join(target_parts_after[:target_count_after])

        le_target_text = f'{target_text_before[:-1]} <T> {target_quote_text} </T> {target_text_after[1:]}'

        return le_source_text, le_target_text

    def __predict_link(self, pairs: List[Tuple[str, str]]) -> List[float]:
        """
        Predict the probability of each pair of belonging together, i.e. the quote in target text passage is taken from
        the corresponding source text passage.
        :param pairs: A list of pairs of strings to be predicted.
        :return: A list probabilities with a probability for each pair.
        """

        if len(pairs) == 0:
            return []

        if len(pairs) > 1000:
            logging.warning(f'Too many pairs: {len(pairs)}')
            return []

        test_data = self.linking_vectorizer.vectorize(pairs)
        prediction = self.linking_model.predict(test_data, verbose=0)
        prediction_logits = prediction.logits
        probs = tf.nn.softmax(prediction_logits, axis=1).numpy()
        preds = [row[1] for row in probs]
        return preds

    def __search_single_word(self, sq: Quote, source_text: str) -> List[Tuple[int, int]]:
        """
        Search for the given quote in the given source text and return a list of candidate start and end character
        positions.
        :param sq: The quote to search for
        :param source_text: The source text
        :return: A list of candidate start and end character positions
        """
        # First, look for an exact match
        re_matches = Helper.strict_match(sq.text, source_text)
        strict_matches_count = len(re_matches)

        # if there are 1 or more exact matches, return them all
        if strict_matches_count > 0:
            result = []

            for re_match in re_matches:
                result.append((re_match.start(), re_match.end()))

            return result

        # if there were no exact matches, make a fuzzy search, for details, see :meth:`proquo.core.Helper.fuzzy_match`
        # for details
        fuzzy_candidates = Helper.fuzzy_match(sq.text, 0, len(source_text), self.hashes, self.SCORE_CUTOFF)
        return fuzzy_candidates

    def __search_multi_word(self, short_matches: List[Match], sq: Quote, source_text: str) -> List[Tuple[int, int]]:
        """
        Search for the given quote in the given source text and return a list of candidate start and end character
        positions.
        :param short_matches: The matches from Quid which are used as candidates
        :param sq: A quote
        :param source_text: The source text
        :return: candidate start and end character positions
        """
        # First, look for an exact match
        re_matches = Helper.strict_match(sq.text, source_text)

        # if there are 1 or more exact matches, return them all
        if len(re_matches) > 0:
            result = []

            for re_match in re_matches:
                result.append((re_match.start(), re_match.end()))

            return result

        # if there were no exact matches, we use the short matches from Quid and try to find overlaps
        candidates = []

        for short_match in short_matches:
            overlap_length = Util.calculate_overlap(short_match.target_span.start, short_match.target_span.end,
                                                    sq.start, sq.end)
            quote_length = sq.end - sq.start
            percentage = overlap_length / quote_length

            if percentage >= 0.7:
                candidates.append((short_match.source_span.start, short_match.source_span.end))

        return candidates
