import sys
import itertools
import re
from typing import Optional, List, Tuple
from quid.match.Match import Match
from quid.match.MatchSpan import MatchSpan

from proquo.core import Helper
from proquo.match.MatchRef import MatchRef
from proquo.core.Quote import Quote
from proquo.core.QuoteRef import QuoteRef
from proquo.core.Reference import Reference
import numpy as np
from sklearn.cluster import SpectralClustering
import tensorflow as tf
from transformers.modeling_tf_utils import TFPreTrainedModel
from tensorflow.keras.models import Model

from proquo.model.reference.ReferenceVectorizer import ReferenceVectorizer
from proquo.model.relation.RelationVectorizerBert import RelationVectorizerBert

from kpcommons import Footnote, Util


# noinspection PyMethodMayBeStatic
class ProQuo:
    # Todo: Make these customizable
    # References
    MAX_BRACKET_LENGTH = 25
    LONG_MIN_LENGTH = 5
    REF_EXAMPLE_COUNT = 5
    # Relation
    REF_MIN_PROB: float = 0.7
    REL_MIN_PROB: float = 0.5
    REL_MAX_DISTANCE = 100
    REL_MAX_WORDS: int = 120
    # Linking
    WITHOUT_REF_SEARCH_RADIUS = 500
    # Fuzzy matching
    SCORE_CUTOFF: int = 0.85

    def __init__(self, reference_model: Model, reference_vectorizer: ReferenceVectorizer,
                 relation_model: TFPreTrainedModel, relation_vectorizer: RelationVectorizerBert, open_quote: str = None,
                 close_quote: str = None):
        """
        :param reference_model: The model for reference classification
        :param reference_vectorizer: The vectorizer to use to tokenize and encode inputs for the reference model
        :param relation_model: The model for relation classification
        :param relation_vectorizer: The vectorizer to use to tokenize and encode inputs for the relation model
        :param open_quote: Character used for opening quotation marks
        :param close_quote: Character used for closing quotation marks
        """
        self.reference_model = reference_model
        self.reference_vectorizer = reference_vectorizer
        self.relation_model = relation_model
        self.relation_vectorizer = relation_vectorizer
        self.source_cache = {}
        self.hashes = None
        self.parallel_print = False
        self.parallel_print_first_page = 0
        self.parallel_print_last_page = 0
        self.open_quote = open_quote
        self.close_quote = close_quote

    def compare(self, source_text: str, target_text: str, quid_matches: List[Match],
                parallel_print=False, parallel_print_first_page=0, parallel_print_last_page=0)\
            -> List[MatchRef]:
        """
        Compare the two input texts and return a list of matching sequences.
        :param source_text: A source text
        :param target_text: A target text
        :param quid_matches: A list of matches from Quid to be used as candidates for short matches
        :param parallel_print: True if the source text is a parallel print edition
        :param parallel_print_last_page: The first page on which the parallel print edition starts
        :param parallel_print_first_page: The last page on which the parallel print edition appears
        :return: A list of matches
        """

        source_text = Helper.clean_text(source_text)

        # Check if text was already processed and use cached version for speed up
        source_text_hash = hash(source_text)
        if source_text_hash in self.source_cache:
            self.hashes = self.source_cache[source_text_hash]
        else:
            self.hashes = Helper.init_lsh_hashes(source_text)
            self.source_cache[source_text_hash] = self.hashes

        self.parallel_print = parallel_print
        self.parallel_print_first_page = parallel_print_first_page
        self.parallel_print_last_page = parallel_print_last_page

        # sort Quid matches into two lists: long and short matches
        long_matches = self.__filter_long_matches(source_text, quid_matches)
        short_matches = Helper.filter_short_matches(source_text, target_text, quid_matches, self.LONG_MIN_LENGTH)

        matches_with_reference: List[MatchRef] = self.__add_reference_to_match(target_text, long_matches)
        matches_with_reference.sort(key=lambda x: x.target_span.end - x.target_span.start, reverse=True)

        # find the n longest matches with a reference
        longest_matches: List[MatchRef] = []
        for match_with_reference in matches_with_reference:
            if match_with_reference.reference:
                if re.search(r'\d', match_with_reference.reference.text):
                    longest_matches.append(match_with_reference)

            if len(longest_matches) >= self.REF_EXAMPLE_COUNT:
                break

        prototypical_reference = self.__get_prototypical_reference(longest_matches)
        all_references: List[Reference] = self.__get_references(target_text, prototypical_reference)
        all_quotes: List[Quote] = Helper.get_quotations(target_text, self.LONG_MIN_LENGTH, self.open_quote,
                                                        self.close_quote)
        footnote_ranges = Footnote.get_footnote_ranges_without_offset(target_text)

        # we are only interested in quotes and references in the running text
        main_references = []
        for ref in all_references:
            if not Footnote.is_range_in_ranges(ref.start, ref.end, footnote_ranges):
                main_references.append(ref)

        main_quotes = []
        for q in all_quotes:
            if not Footnote.is_range_in_ranges(q.start, q.end, footnote_ranges):
                main_quotes.append(q)

        main_quotes = self.__filter_quotes_not_in_source(main_quotes, 0, len(source_text))

        main_references.sort(key=lambda x: x.start)
        main_quotes.sort(key=lambda x: x.start)

        quote_ref_combos_main = self.__get_combinations(target_text, main_references, main_quotes, footnote_ranges)

        quote_ref_combos: List[QuoteRef] = []
        quote_ref_combos.extend(quote_ref_combos_main)

        short_quotes: List[QuoteRef] = self.__get_short_quotes(quote_ref_combos)
        short_quotes = self.__filter_duplicates(short_quotes)

        matches_with_reference.sort(key=lambda x: 0 if x.reference is None else x.reference.page)
        result_matches: List[MatchRef] = []

        page_size, first_page_known_pos, first_page_nr = self.__get_page_size(matches_with_reference)

        # quotes with a reference are processed first
        for sq in short_quotes:
            start, end, page_known_pos = self.__get_quote_range_with_ref(sq, page_size, first_page_known_pos,
                                                                         first_page_nr, len(source_text))

            match_len = len(sq.quote.text.split())

            if match_len == 1:
                quote_source_start, quote_source_end = self.__search_single_word(sq.quote, source_text, start, end,
                                                                                 page_known_pos)
            else:
                quote_source_start, quote_source_end = self.__search_multi_word(short_matches, sq, start, end,
                                                                                source_text)

            if quote_source_start > -1:
                quote_source_text = source_text[quote_source_start:quote_source_end]
                source_span = MatchSpan(quote_source_start, quote_source_end, quote_source_text)
                target_span = MatchSpan(sq.quote.start, sq.quote.end, sq.quote.text)
                match = MatchRef(source_span, target_span, sq.reference)
                result_matches.append(match)

        # then quotes without a reference are processed
        short_quotes_without_ref = []

        for mq in main_quotes:
            found = False

            for sq in short_quotes:
                if sq.quote.start == mq.start and sq.quote.end == mq.end:
                    found = True
                    break

            if not found:
                short_quotes_without_ref.append(QuoteRef(mq, None, ''))

        # add result matches
        matches_with_reference.extend(result_matches)
        matches_with_ref_in_appearance = sorted(matches_with_reference, key=lambda x: x.target_span.start)

        # search for short quotes without a reference
        for sq in short_quotes_without_ref:
            start, end, page_known_pos = self.__get_quote_range_without_ref(sq, matches_with_ref_in_appearance,
                                                                            len(source_text), page_size)

            quote_source_start = -1
            quote_source_end = -1
            match_len = len(sq.quote.text.split())

            if match_len == 1:
                if page_known_pos > -1:
                    quote_source_start, quote_source_end = self.__search_single_word(sq.quote, source_text, start, end,
                                                                                     page_known_pos)
            else:
                quote_source_start, quote_source_end = self.__search_multi_word(short_matches, sq, start, end,
                                                                                source_text)

            if quote_source_start > -1:
                quote_source_text = source_text[quote_source_start:quote_source_end]

                source_span = MatchSpan(quote_source_start, quote_source_end, quote_source_text)
                target_span = MatchSpan(sq.quote.start, sq.quote.end, sq.quote.text)
                match = MatchRef(source_span, target_span, sq.reference)
                result_matches.append(match)

        return result_matches

    def __predict_ref(self, references_1: List[str], references_2: List[str]) -> List[float]:
        """
        Takes two lists of reference strings and returns the probabilities of two references having the same style.
        :param references_1: List of reference strings
        :param references_2: List of references strings
        :return: Probabilities of two references having the same style
        """
        if len(references_1) == 0 or len(references_2) == 0:
            return []

        test_data_x_1 = self.reference_vectorizer.vectorize(references_1)
        test_data_x_2 = self.reference_vectorizer.vectorize(references_2)
        preds = list(self.reference_model.predict([test_data_x_1, test_data_x_2], verbose=0).ravel())
        return preds

    def __predict_rel(self, quote_ref_combos: List[QuoteRef]) -> List[float]:
        """
        Takes a list of combinations of quotation and reference and predicts the probability for each combination that
        the quotation and reference belong together.
        :param quote_ref_combos: A list of combinations of quotation and reference
        :return: A list of probabilities
        """

        if len(quote_ref_combos) == 0:
            return []

        sentences = []

        for qrc in quote_ref_combos:
            text = qrc.text
            text = re.sub(fr'([{self.open_quote}{self.close_quote}])', r' \1 ', text, flags=re.DOTALL)
            sentences.append(text)

        test_data = self.relation_vectorizer.vectorize(sentences)

        prediction = self.relation_model.predict(test_data, verbose=0)
        prediction_logits = prediction.logits
        probs = tf.nn.softmax(prediction_logits, axis=1).numpy()
        preds = [row[1] for row in probs]

        return preds

    def __filter_long_matches(self, input_text: str, matches: List[Match]) -> List[Match]:
        """
        Takes a list of matches and returns a new list which only contains matches which are longer then a certain
        lower limit.
        :param input_text: The input text
        :param matches: A list of matches
        :return: A list of matches which fulfill the length requirement
        """
        result = []
        for match in matches:
            text = input_text[match.source_span.start:match.source_span.end]
            length = len(text.split())

            if length >= self.LONG_MIN_LENGTH:
                result.append(match)

        return result

    def __add_reference_to_match(self, input_text: str, matches: List[Match]) -> List[MatchRef]:
        """
        Goes through all matches and tries to find a reference in parentheses after the match within a certain distance.
        :param input_text: A text
        :param matches: A list of matches
        :return: A list of matches with references
        """

        result: List[MatchRef] = []

        for match in matches:
            match_ref = MatchRef.from_match(match)
            end = match.target_span.end
            context_text = input_text[end:end + 20]

            re_match = re.search(r'\((.+?)\)', context_text)
            if re_match:
                ref_start = re_match.start(1)
                ref_end = re_match.end(1)
                ref_text = re_match.group(1)
                page_nr = self.__extract_page_from_reference(ref_text)

                reference = Reference(ref_start, ref_end, ref_text, page_nr)
                match_ref.reference = reference

            result.append(match_ref)

        return result

    def __get_prototypical_reference(self, match_ref_examples: List[MatchRef]) -> str:
        """
        From the up to five examples, the best example is identified.
        :param match_ref_examples: A list of matches with references
        :return: A prototypical reference string.
        """
        num_examples = len(match_ref_examples)

        if num_examples == 0:
            return ''

        match_ref_ex_with_id = []

        # as a default, we just use the first example
        index = 0

        # To identify the best example, we need more than two examples
        if num_examples > 2:
            for pos, mre in enumerate(match_ref_examples):
                match_ref_ex_with_id.append((pos, mre))

            match_ref_combinations = itertools.combinations(match_ref_ex_with_id, 2)
            sentences_1: List[str] = []
            sentences_2: List[str] = []
            combinations = []

            perm: Tuple[Tuple[int, MatchRef], Tuple[int, MatchRef]]
            for perm in match_ref_combinations:
                sentences_1.append(perm[0][1].reference.text)
                sentences_2.append(perm[1][1].reference.text)
                combinations.append((perm[0], perm[1]))

            if len(sentences_1) == 0 or len(sentences_2) == 0:
                return ''

            preds = self.__predict_ref(sentences_1, sentences_2)
            num_examples = len(match_ref_examples)

            matrix = np.eye(num_examples, dtype=float)

            for perm, pred in zip(combinations, preds):
                x = perm[0][0]
                y = perm[1][0]
                # matrix has to be symmetrical
                matrix[x][y] = pred
                matrix[y][x] = pred

            labels = SpectralClustering(2, affinity='precomputed').fit_predict(matrix)
            labels = labels.tolist()

            num_occ_cluster_0 = labels.count(0)
            num_occ_cluster_1 = labels.count(1)

            if num_occ_cluster_0 > num_occ_cluster_1:
                index = labels.index(0)
            else:
                index = labels.index(1)

        best_bibl = match_ref_examples[index]
        return best_bibl.reference.text

    def __get_references(self, input_text: str, prototypical_reference: str) -> List[Reference]:
        """
        All text in parentheses is compared to the prototypical example to identify all references in the text.
        :param input_text: A text
        :param prototypical_reference: A prototypical reference string
        :return: A list of all references in the text which are similar to the given examples.
        """

        if not prototypical_reference:
            return []

        bracket_positions = {}
        stack = []

        for i, c in enumerate(input_text):
            if c == '(':
                stack.append(i)
            elif c == ')':
                if len(stack) > 0:
                    # There will be errors, so we just ignore them
                    bracket_positions[stack.pop()] = i

        possible_references = []

        for start, end in bracket_positions.items():
            if end - start > self.MAX_BRACKET_LENGTH:
                continue

            ref_text = input_text[start + 1:end]
            # TODO: resolve ebd.
            page_nr = self.__extract_page_from_reference(ref_text)
            possible_references.append(Reference(start + 1, end, input_text[start + 1:end], page_nr))

        possible_permutations = itertools.product([x.text for x in possible_references], [prototypical_reference])

        poss_bibl_sentences_1 = []
        poss_bibl_sentences_2 = []

        for perm in list(possible_permutations):
            poss_bibl_sentences_1.append(perm[0])
            poss_bibl_sentences_2.append(perm[1])

        preds_2 = self.__predict_ref(poss_bibl_sentences_1, poss_bibl_sentences_2)

        references: List[Reference] = []

        for pr, pred in zip(possible_references, preds_2):
            if pred >= self.REF_MIN_PROB:
                references.append(pr)

        return references

    def __replace_other_ref(self, input_text: str, references: List[Reference], start: int, end: int) -> str:
        """
        Replace reference strings in the given text with a tag in the range between start and end.
        :param input_text: A text
        :param references: A list of references
        :param start: A start character position
        :param end: An end character position
        :return: The modified input text
        """
        other_refs = []

        for ref in references:
            if ref.start >= start and ref.end <= end:
                other_refs.append(ref)

        text = input_text[start:end]
        other_refs.sort(key=lambda x: x.start, reverse=True)

        for ref in other_refs:
            text = f'{text[:ref.start - start]} <OREF> {text[ref.end - start:]}'

        text = re.sub(r'\[\[\[((?:.|\n)+?)]]]', '', text, flags=re.DOTALL)

        return text

    def __get_combinations(self, input_text: str, references: List[Reference], quotes: List[Quote],
                           footnote_ranges: Optional[List[Tuple[int, int]]]) -> List[QuoteRef]:
        """
        Generate all combinations of quotes and reference within a certain distance, excluding footnotes.
        :param input_text: The input text
        :param references: A list of references
        :param quotes: A list of quotes
        :param footnote_ranges: A list of footnote ranges
        :return: A list of combinations of quotes and references. Additionally, a text is created with the quote tagged
        and the reference replaced with a tag.
        """

        my_permutations = itertools.product(quotes, references)

        result: List[QuoteRef] = []

        for perm in my_permutations:
            quote = perm[0]
            reference = perm[1]

            if quote.start < reference.end:
                start = quote.start
                end = reference.end
                between_start = quote.end
                between_end = reference.start
                words_in_fn_count = 0

                if footnote_ranges:
                    words_in_fn_count = self.__count_words_in_footnotes(input_text, footnote_ranges, start, end)

                dist = len(input_text[between_start:between_end].split()) - words_in_fn_count
                if dist > self.REL_MAX_DISTANCE:
                    continue

                text_replaced = self.__replace_other_ref(input_text, references, quote.end, reference.start)
                text = f' <Q> {input_text[quote.start:quote.end]} </Q> {text_replaced[1:]} <REF> '
            else:
                start = reference.start
                end = quote.end
                between_start = reference.end
                between_end = quote.start
                words_in_fn_count = 0

                if footnote_ranges:
                    words_in_fn_count = self.__count_words_in_footnotes(input_text, footnote_ranges, start, end)

                dist = len(input_text[between_start:between_end].split()) - words_in_fn_count
                if dist > self.REL_MAX_DISTANCE:
                    continue

                text_replaced = self.__replace_other_ref(input_text, references, reference.end, quote.start)
                text = f' <REF> {text_replaced[:-1]} <Q> {input_text[quote.start:quote.end]} </Q> '

            length = len(text.split())

            if length > self.REL_MAX_WORDS:
                continue

            rest_len = self.REL_MAX_WORDS - length

            parts_before = input_text[:start].split()
            parts_after = input_text[end:].split()

            parts_before_count = len(parts_before)
            parts_after_count = len(parts_after)

            count_before = min(round(rest_len / 2), parts_before_count)
            count_after = min(rest_len - count_before, parts_after_count)

            text_before = ''
            temp_end = start

            for i in range(len(parts_before) - 1, len(parts_before) - 1 - count_before, -1):
                part = parts_before[i]
                part_len = len(part)
                temp_start = temp_end - 1 - part_len

                if not footnote_ranges or not Footnote.is_range_in_ranges(temp_start, temp_end, footnote_ranges):
                    text_before = f'{parts_before[i]} {text_before}'

                temp_end = temp_start

            text_after = ''
            temp_start = end

            for i in range(0, count_after):
                part = parts_after[i]
                part_len = len(part)
                temp_end = temp_start + 1 + part_len

                if not footnote_ranges or not Footnote.is_range_in_ranges(temp_start, temp_end, footnote_ranges):
                    text_after += f' {parts_after[i]}'

                temp_start = temp_end

            text_before_replaced = self.__replace_other_ref(input_text, references, start - len(text_before), start)
            text_after_replaced = self.__replace_other_ref(input_text, references, end, end + len(text_after))

            if quote.start < reference.end:
                text = f'{text_before_replaced[:-1]} {text[1:]} {text_after_replaced}'
            else:
                text = f'{text_before_replaced} {text[:-1]} {text_after_replaced[1:]}'

            result.append(QuoteRef(quote, reference, text))

        return result

    def __get_short_quotes(self, quote_ref_combos: List[QuoteRef]) -> List[QuoteRef]:
        """
        Takes a list of combinations of quotation and reference and returns a new list which only contains combinations
        which are have a certain probability of belonging together.
        :param quote_ref_combos: A list of combinations of quotation and reference
        :return: A filtered list of combinations of quotation and reference
        """
        preds = self.__predict_rel(quote_ref_combos)
        result = []

        for qrc, pred in zip(quote_ref_combos, preds):
            if pred >= self.REL_MIN_PROB:
                qrc.pred = pred
                result.append(qrc)

        return result

    def __filter_quotes_not_in_source(self, quotes: List[Quote], start: int, end: int) -> List[Quote]:
        """
        Create a list of quotes from the given list of quotes which only contains quotes which are longer than a single
        word or could be found the source text by fuzzing matching.
        :param quotes: A list of quotes
        :param start: A start character position
        :param end: A end character position
        :return: A list of the remaining quotes
        """
        result: List[Quote] = []

        for quote in quotes:
            if len(quote.text.split()) > 1:
                result.append(quote)
                continue

            candidates = Helper.fuzzy_match(quote.text, start, end, self.hashes, self.SCORE_CUTOFF)
            if len(candidates) == 0:
                continue

            result.append(quote)

        return result

    def __filter_duplicates(self, short_quotes: List[QuoteRef]) -> List[QuoteRef]:
        """
        Create a list only containing non overlapping quotes.
        :param short_quotes: The input list of quotes
        :return: The resulting list of quotes
        """
        result = []

        for sq in short_quotes:
            found = False
            replace_pos = -1

            for pos, r in enumerate(result):
                if r.quote.start == sq.quote.start and r.quote.end == sq.quote.end:
                    found = True

                    if sq.pred > r.pred:
                        replace_pos = pos
                    break

            if not found:
                result.append(sq)
            elif replace_pos > -1:
                result[replace_pos] = sq

        return result

    def __calc_page_offset_parallel_print(self, start: int, end: int) -> int:
        """
        Only needed for parallel print editions.
        :param start: A start page
        :param end: An end page
        :return: The number of pages to subtract
        """
        if end > start:
            if self.parallel_print_first_page < end <= self.parallel_print_last_page:
                return (end - max(self.parallel_print_first_page, start)) // 2
            elif self.parallel_print_first_page < start < self.parallel_print_last_page:
                return (self.parallel_print_last_page - start) // 2
        else:
            if self.parallel_print_first_page < start < self.parallel_print_last_page:
                return (start - max(self.parallel_print_first_page, end)) // 2
            elif self.parallel_print_first_page < end < self.parallel_print_last_page:
                return (self.parallel_print_last_page - end) // 2

        return 0

    def __extract_page_from_reference(self, text: str) -> int:
        """
        A simple approach to extracting a page number from a reference string.
        :param text: A reference string
        :return: The extracted page number
        """

        page_nr = 0

        re_match = re.search(r'S\. ?(\d+)', text)
        if re_match:
            page_nr = int(re_match.group(1))
            return page_nr

        re_match = re.search(r'^(\d+)', text)
        if re_match:
            page_nr = int(re_match.group(1))
            return page_nr

        re_match = re.search(r'\W(\d+)', text)
        if re_match:
            page_nr = int(re_match.group(1))
            return page_nr

        # page_nr = self.__resolve_non_number_page(text, prev_match_with_ref)
        return page_nr

    # def __resolve_non_number_page(self, text: str, prev_match_with_ref: MatchRef) -> int:
    #     if not prev_match_with_ref:
    #         return 0
    #
    #     if text.startswith('ebd'):
    #         return prev_match_with_ref.reference.page
    #
    #     return 0

    def __count_words_in_footnotes(self, input_text: str, footnote_ranges: List[Tuple[int, int]], start: int, end: int)\
            -> int:
        """
        Count the number of words in footnotes in the given range.
        :param input_text: The input text
        :param footnote_ranges: The list of footnote ranges
        :param start: A start character position
        :param end: An end character position
        :return: The number of words in footnotes
        """

        count = 0

        for fr in footnote_ranges:
            if start <= fr[0] < end:
                text = input_text[fr[0]:fr[1]]
                count += len(text.split())

        return count

    def __get_page_size(self, matches_with_reference: List[MatchRef]) -> Tuple[int, int, int]:
        """
        Estimate the page size of the source text from the long matches and their references (from Quid).
        This is done by using the quotes which appear first and last in the source text and estimate a page size
        based on the distance of these two quotes and the page numbers.
        :param matches_with_reference: A list of matches and their references
        :return: A tuple with the page size, the character start position of the first quote and the page number
        """
        mwr_sorted = sorted(matches_with_reference, key=lambda x: x.source_span.start)

        start = -1
        end = -1
        first_page = 0
        last_page = 0

        for match_ref in mwr_sorted:
            if match_ref.reference and match_ref.reference.page > 0:
                if start == -1:
                    start = match_ref.source_span.start
                    first_page = match_ref.reference.page
                elif first_page > match_ref.reference.page:
                    start = -1

        for match_ref in reversed(mwr_sorted):
            if match_ref.reference and match_ref.reference.page > 0:
                if end == -1:
                    end = match_ref.source_span.end
                    last_page = match_ref.reference.page
                elif last_page < match_ref.reference.page:
                    end = -1

        page_size = 0

        if self.parallel_print:
            page_diff = last_page - first_page - self.__calc_page_offset_parallel_print(first_page, last_page)
        else:
            page_diff = last_page - first_page

        if 0 < first_page != last_page > 0:
            page_size = ((end - start) // page_diff)

        return page_size, start, first_page

    def __get_quote_range_with_ref(self, sq: QuoteRef, page_size: int, first_page_known_pos: int, first_page_nr: int,
                                   source_text_len: int):
        """
        Tries to estimate the best range in the source text to search for the quotation.
        :param sq: A quote with a reference
        :param page_size: The page size
        :param first_page_known_pos: The character position of the first match
        :param first_page_nr: The page number of the first page
        :param source_text_len: Length of the source text
        :return: A tuple of: The character start and end positions of the range in the source text in which we assume
        the quote can be found. And the estimated position of where the quote is assumed to be found.
        """
        start = 0
        end = source_text_len
        page_known_pos = -1

        if sq.reference.page > 0:
            if page_size > 0 and first_page_nr > 0:

                if self.parallel_print:
                    page_diff = sq.reference.page - first_page_nr - \
                                self.__calc_page_offset_parallel_print(first_page_nr, sq.reference.page)
                else:
                    page_diff = sq.reference.page - first_page_nr

                page_known_pos = first_page_known_pos + (page_diff * page_size)
                start = max(0, page_known_pos - page_size)
                end = min(source_text_len, page_known_pos + page_size)

        # in this special case we search the whole text
        if end <= start:
            start = 0
            end = source_text_len

        return start, end, page_known_pos

    def __get_quote_range_without_ref(self, sq: QuoteRef, matches_with_reference: List[MatchRef], source_text_len: int,
                                      page_size: int) -> Tuple[int, int, int]:
        """
        Tries to estimate the best range in the source text to search for the quotation.
        :param sq: A quote without a references
        :param matches_with_reference: Matches with a reference
        :param source_text_len: The length of the source text
        :param page_size: The page size
        :return: A tuple of: The character start and end positions of the range in which we assume the quote can be
        found. And the estimated position of where the quote is assumed to be found.
        """
        mwr_best = None
        best_dist = sys.maxsize

        for pos, match_with_reference in enumerate(matches_with_reference):
            if not match_with_reference.reference:
                continue

            mwr_start = max(0, match_with_reference.target_span.start - self.WITHOUT_REF_SEARCH_RADIUS)
            mwr_end = min(source_text_len, match_with_reference.target_span.end + self.WITHOUT_REF_SEARCH_RADIUS)

            new_dist = sys.maxsize

            if mwr_start <= sq.quote.start <= match_with_reference.target_span.start:
                new_dist = match_with_reference.target_span.start - sq.quote.end
            elif match_with_reference.target_span.end <= sq.quote.start <= mwr_end:
                new_dist = sq.quote.start - match_with_reference.target_span.end

            if new_dist < best_dist:
                best_dist = new_dist
                mwr_best = match_with_reference

        start = 0
        end = source_text_len
        page_known_pos = -1

        if mwr_best:
            if page_size > 0:
                start = max(0, mwr_best.source_span.start - page_size)
                end = min(source_text_len, mwr_best.source_span.end + page_size)
                page_known_pos = mwr_best.source_span.start + ((mwr_best.source_span.end - mwr_best.source_span.start) // 2)

        return start, end, page_known_pos

    def __search_single_word(self, quote: Quote, source_text: str, range_start: int, range_end: int,
                             page_known_pos: int) -> Tuple[int, int]:
        """
        Search for the given quote in the given source text.
        :param quote: A quote
        :param source_text: The source text
        :param range_start: The character start position of the range to search in
        :param range_end: The character end position of the range to search in
        :param page_known_pos:
        :return: A tuple consisting of the start and end character positions if a match was found. Otherwise (-1, -1)
        """

        source_search_space = source_text[range_start:range_end]
        re_matches = Helper.strict_match(quote.text, source_search_space)
        strict_matches_count = len(re_matches)

        if strict_matches_count == 0:
            fuzzy_candidates = Helper.fuzzy_match(quote.text, range_start, range_end, self.hashes,
                                                  self.SCORE_CUTOFF)

            if len(fuzzy_candidates) == 1:
                return fuzzy_candidates[0][0], fuzzy_candidates[0][1]
            elif len(fuzzy_candidates) > 1:
                smallest_dist = sys.maxsize
                best_match_start_pos = 0
                best_match_end_pos = 0

                for fc in fuzzy_candidates:
                    # TODO: Is start ideal? Maybe compare start and end
                    m_start = fc[0]
                    diff = abs(page_known_pos - m_start)
                    if diff < smallest_dist:
                        smallest_dist = diff
                        best_match_start_pos = m_start
                        best_match_end_pos = fc[1]

                return best_match_start_pos, best_match_end_pos

        elif strict_matches_count == 1:
            re_match = re_matches[0]

            if re_match:
                return re_match.start() + range_start, re_match.end() + range_start

        elif page_known_pos > -1:
            smallest_dist = sys.maxsize
            best_match_start_pos = -1
            best_match_end_pos = -1

            for m in re_matches:
                # TODO: Is start ideal? Maybe compare start and end
                m_start = m.start() + range_start
                diff = abs(page_known_pos - m_start)
                if diff < smallest_dist:
                    smallest_dist = diff
                    best_match_start_pos = m_start
                    best_match_end_pos = m.end() + range_start

            return best_match_start_pos, best_match_end_pos

        return -1, -1

    def __search_multi_word(self, short_matches: List[Match], sq: QuoteRef, range_start: int, range_end: int,
                            source_text: str) -> Tuple[int, int]:
        """
        Search for the given quote in the given source text. First for an exact match and then for a fuzzy match.
        :param short_matches: The matches from Quid which are used as candidates
        :param sq: A quote
        :param range_start: The character start position of the range to search in
        :param range_end: The character end position of the range to search in
        :param source_text: The source text
        :return: A tuple consisting of the start and end character positions if a match was found. Otherwise (-1, -1)
        """

        search_space = source_text[range_start:range_end]
        re_matches = Helper.strict_match(sq.quote.text, search_space)

        if len(re_matches) > 1:
            return -1, -1

        if len(re_matches) == 1:
            return re_matches[0].start() + range_start, re_matches[0].end() + range_start
        elif len(re_matches) == 0:
            re_matches = Helper.strict_match(sq.quote.text, source_text)
            if len(re_matches) > 1:
                return -1, -1

            if len(re_matches) == 1:
                return re_matches[0].start(), re_matches[0].end()

        candidates = []

        for short_match in short_matches:
            overlap_length = Util.calculate_overlap(short_match.target_span.start, short_match.target_span.end,
                                                    sq.quote.start, sq.quote.end)
            quote_length = sq.quote.end - sq.quote.start
            percentage = overlap_length / quote_length

            if percentage >= 0.7:
                candidates.append(short_match)

        candidates_count = len(candidates)

        if candidates_count == 0:
            return -1, -1
        elif candidates_count == 1:
            return candidates[0].source_span.start, candidates[0].source_span.end
        else:
            filtered_candidates = []

            for c in candidates:
                if c.source_span.start >= range_start and c.source_span.end <= range_end:
                    filtered_candidates.append(c)

            if len(filtered_candidates) == 1:
                return filtered_candidates[0].source_span.start, filtered_candidates[0].source_span.end

        return -1, -1
