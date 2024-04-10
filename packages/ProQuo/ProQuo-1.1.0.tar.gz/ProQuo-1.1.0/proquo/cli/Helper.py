import multiprocessing
from os import listdir
from os.path import join, isfile
from quid.core.Quid import Quid


def __run_quid(source_file_content, target_file_content, min_match_length, keep_ambiguous_matches,
               cached_min_length_match_positions, cached_hashes):
    quid = Quid(min_match_length=min_match_length, keep_ambiguous_matches=keep_ambiguous_matches)
    matches = quid.compare(source_file_content, target_file_content, cached_min_length_match_positions, cached_hashes)
    return matches


def get_quid_matches_mp(source_file_content, target_path, num_of_processes, min_match_length, keep_ambiguous_matches):
    quid = Quid(min_match_length=min_match_length, keep_ambiguous_matches=keep_ambiguous_matches)
    min_length_match_positions, hashes = quid.prepare_source_data(source_file_content)
    pool = multiprocessing.Pool(num_of_processes)

    results = []
    for file_or_folder in listdir(target_path):
        full_path = join(target_path, file_or_folder)

        if isfile(full_path) and full_path.endswith(".txt"):
            with open(full_path, 'r', encoding='utf-8') as target_file:
                target_file_content = target_file.read()

            result = pool.apply_async(__run_quid, args=(source_file_content, target_file_content,
                                                        min_match_length, keep_ambiguous_matches,
                                                        min_length_match_positions, hashes))
            results.append(result)

    pool.close()
    pool.join()

    result_matches = []
    for result in results:
        result_matches.append(result.get())

    return result_matches
