import re
from typing import List, Tuple
import typing
from datasketch import MinHashLSH, MinHash
from quid.match.Match import Match
from rapidfuzz.distance import Levenshtein
from proquo.core.Quote import Quote
import logging


HASH_PERM: int = 128
LSH_THRESHOLD: float = 0.70

# 1. " und "
# 2. „ und “
# 3. „ und "
# 4. “ und “
# 5. » und «
# 6. « und »
# 7. ‘ und ’
QUOTATION_MARKS = [('"', '"'), ('\u201E', '\u201C'), ('\u201E', '"'), ('\u201C', '\u201C'),
                   ('\u00BB', '\u00AB'), ('\u00AB', '\u00BB'), ('\u2018', '\u2019')]


def filter_short_matches(source_text: str, target_text: str, matches: List[Match], min_length: int) -> List[Match]:
    """
    Takes a list of matches and only returns the ones which are shorter than the given length in words.
    :param source_text: A source text
    :param target_text: A target text
    :param matches: A list of matches
    :param min_length: The maximum length in words
    :return: A list of matches which fulfill the criteria
    """
    result: List[Match] = []
    for match in matches:
        match_source_text = source_text[match.source_span.start:match.source_span.end]
        match_target_text = target_text[match.target_span.start:match.target_span.end]
        source_length = len(match_source_text.split())
        target_length = len(match_target_text.split())

        if source_length < min_length or target_length < min_length:
            result.append(match)

    return result


def get_quotations(input_text: str, max_length: int, quote_open: str = None, quote_close: str = None) -> List[Quote]:
    """
    Search for text in quotation marks which is shorter than the given maximum length in words.
    :param quote_close: The opening quotation mark
    :param quote_open: The closing quotation mark
    :param input_text: The input length
    :param max_length: The maximum length in words
    :return: A list of found quotations
    """

    if not quote_open or not quote_close:
        quote_open, quote_close = __determine_quotation_mark(input_text)

    if not quote_open or not quote_close:
        return []

    quotes: List[Quote] = []

    for re_match in re.finditer(fr'{quote_open}([^{quote_open}]+){quote_close}', input_text):
        start = re_match.span(1)[0]
        end = re_match.span(1)[1]
        text = re_match.group(1)

        if len(text.split()) < max_length:
            quotes.append(Quote(start, end, text))

    return quotes


def __determine_quotation_mark(input_text: str) -> Tuple[str, str]:
    quote_open = ''
    quote_close = ''
    best_count = 0

    for qp in QUOTATION_MARKS:
        match_count = sum(1 for _ in re.finditer(fr'{qp[0]}\b([^{qp[0]}]+){qp[1]}', input_text))

        if match_count > 0:
            open_count = input_text.count(qp[0])
            close_count = input_text.count(qp[1])

            if open_count != 0 and close_count == 0:
                logging.warning(f'Found only left quotation marks for {qp[0]} and {qp[1]}!')
                continue

            if open_count == 0 and close_count != 0:
                logging.warning(f'Found only right quotation marks for {qp[0]} and {qp[1]}!')
                continue

            if open_count != close_count:
                logging.warning(f'Found {match_count} quotes but quote left and right count are not the same:'
                                f' {open_count} vs. {close_count} for {qp[0]} and {qp[1]}')

            if match_count > best_count:
                best_count = match_count
                quote_open = qp[0]
                quote_close = qp[1]

    if not quote_open or not quote_close:
        logging.warning('No quote type could be determined!')
    else:
        logging.info(f'Best quote type: {quote_open} and {quote_close}')

    return quote_open, quote_close


def clean_text(input_text: str) -> str:
    """
    Clean the given text without changing the length, i.e. replace all special characters with spaces.
    :param input_text: The input text
    :return: The cleaned text
    """
    output_text = re.sub('(\\[\\.\\.\\.]|\\[…]|\\.\\.\\.|…)', lambda x: ' ' * len(x.group(1)), input_text)
    output_text = re.sub(f'[^a-zA-Z\\däüöÄÜÖß\n ]', ' ', output_text)

    if len(input_text) != len(output_text):
        raise Exception('Length of source text changed')

    return output_text.lower()


def __clean_single_word(input_text: str) -> str:
    """
    Clean the given text by removing special characters.
    :param input_text: The input text
    :return: The cleaned text
    """
    output_text = re.sub(f'[^a-zA-Z\\däüöÄÜÖß\n ]', '', input_text)
    return output_text.lower()


def normalize_special_chars(input_word: str) -> str:
    """
    Replace some character combinations with another version to normalize umlauts.
    :param input_word:
    :return:
    """
    input_word = input_word.replace('ß', 'ss')
    input_word = input_word.replace('ä', 'ae')
    input_word = input_word.replace('ö', 'oe')
    input_word = input_word.replace('ü', 'ue')
    input_word = input_word.replace('ey', 'ei')

    input_word = input_word.replace('[', '')
    input_word = input_word.replace(']', '')
    return input_word


def init_lsh_hashes(input_text: str) -> MinHashLSH:
    """
    Tokenizes the input text by whitespace, hashes all tokens and creates a MinHashLSH index.
    :param input_text: The input text
    :return: The initialized MinHashLSH index
    """
    hashes = MinHashLSH(threshold=LSH_THRESHOLD, num_perm=HASH_PERM)

    for match in re.finditer(r'\S+', input_text):
        token = normalize_special_chars(match.group())

        if len(token) > 0:
            text_begin_pos = match.start()
            text_end_pos = match.end()

            token_character_set = set(token)
            token_hash = MinHash(num_perm=HASH_PERM)

            for char in token_character_set:
                token_hash.update(char.encode('utf8'))

            hashes.insert(f'{text_begin_pos}_{text_end_pos}_{token}', token_hash, True)

    return hashes


# TODO: improve with better normalization
def strict_match(word: str, search_space: str) -> List[typing.Match[str]]:
    """
    Match the given word against the given text.
    :param word: The word to search for
    :param search_space: The text in which to search
    :return: A list of matches
    """
    word = clean_text(word)
    # word = self.__normalize_special_chars(word)
    # word = re.sub(' +', ' ', word, flags=re.DOTALL)
    # word = word.strip()
    # search_space = self.__normalize_special_chars(search_space)
    re_matches_iter = re.finditer(r'\b' + re.escape(word) + r'\b', search_space, flags=re.IGNORECASE)
    re_matches = list(re_matches_iter)
    return re_matches


def fuzzy_match(word: str, range_start: int, range_end: int, hashes, score_cutoff: float) -> List[Tuple[int, int]]:
    word = __clean_single_word(word)
    word = normalize_special_chars(word)
    word = re.sub(' +', ' ', word, flags=re.DOTALL)
    word = word.strip()
    word_character_set = set(word)
    word_hash = MinHash(num_perm=HASH_PERM)

    for char in word_character_set:
        word_hash.update(char.encode('utf8'))

    candidates = hashes.query(word_hash)
    candidates_split = []

    for candidate in candidates:
        parts = candidate.split('_')
        candidates_split.append((parts[0], parts[1], parts[2]))

    candidates_split.sort(key=lambda e: int(e[0]))

    result = []

    for candidate in candidates_split:
        c_start = int(candidate[0])
        c_end = int(candidate[1])
        token = candidate[2]
        ratio = Levenshtein.normalized_similarity(word, token)

        if ratio < score_cutoff:
            continue

        if c_start >= range_start and c_end <= range_end:
            result.append((c_start, c_end))

    return result


def remove_short_matches(matches: List[Match], target_file_content):
    """
    Remove matches which are shorter than 5 words.
    :return: The remaining matches.
    """

    if len(matches) == 0:
        return []

    filtered_matches = []

    for match in matches:
        text = target_file_content[match.target_span.start:match.target_span.end]
        length = len(text.split())

        if length >= 5:
            filtered_matches.append(match)

    return filtered_matches


def remove_overlapping_matches(matches: List[Match], target_file_content):
    """
    Remove matches which overlap in the target text.
    :param matches: The input list of matches.
    :return: The remaining matches.
    """

    if len(matches) == 0:
        return []

    matches.sort(key=lambda x: x.target_span.start, reverse=False)

    result: List[Match] = []
    match_position: int = 1
    current_match = matches[0]

    while match_position < len(matches):
        next_match = matches[match_position]

        current_target_match_span = current_match.target_span
        next_target_match_span = next_match.target_span

        current_end_pos = current_target_match_span.end
        next_start_pos = next_target_match_span.start

        if next_start_pos >= current_end_pos:
            result.append(current_match)
            current_match = next_match
        else:
            current_match_text = target_file_content[current_target_match_span.start:current_target_match_span.end]
            next_match_text = target_file_content[next_target_match_span.start:next_target_match_span.end]
            current_token_length = len(current_match_text.split())
            next_token_length = len(next_match_text.split())

            if current_token_length < next_token_length:
                current_match = next_match

        match_position += 1

    result.append(current_match)

    return result
