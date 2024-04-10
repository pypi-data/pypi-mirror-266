from argparse import ArgumentParser
import sys
import logging

from os.path import join, isfile, splitext, basename, isdir, exists
from os import listdir
from datetime import datetime
from pathlib import Path
from typing import List

from quid.core.Quid import Quid
from quid.match.MatchSpan import MatchSpan

from proquo.cli.Helper import get_quid_matches_mp
from proquo.cli.OptionValueCheckAction import OptionValueCheckAction
from proquo.match.MatchRef import MatchRef
from proquo.core.ProQuo import ProQuo
from proquo.core import Helper
from proquo.model.reference.ReferenceModelTrainer import ReferenceModelTrainer
from proquo.model.relation.RelationVectorizerBert import RelationVectorizerBert
import transformers

from proquo.model.reference.ReferenceVectorizer import ReferenceVectorizer
from proquo.testing.reference import TestReference
from proquo.testing.relation import TestRelationBert
from proquo.training.reference import TrainReference
from proquo.training.relation import TrainRelationBert
import re
import json

# only import if tensorflow_text is found. This is hardly ever needed and tensorflow_text is not always easy to install.
try:
    from proquo.training.relation import TrainRelationLstm
    from proquo.testing.relation import TestRelationLstm
except ModuleNotFoundError:
    pass


def __json_encoder_proquo(obj):
    if isinstance(obj, MatchRef):
        result_dict = obj.__dict__

        if not result_dict['reference']:
            del result_dict['reference']

        return result_dict

    if isinstance(obj, MatchSpan):
        result_dict = obj.__dict__

        if not result_dict['text']:
            del result_dict['text']

        return result_dict

    return obj.__dict__


def __process_file(pro_quo, filename, source_file_content, target_file_content, quid_matches_all, quid_matches_long,
                   output_folder_path, source_text_parallel_print, parallel_print_first_page, parallel_print_last_page,
                   export_text, export_ref, output_type, csv_sep):

    logging.info(f'Processing {filename}')
    short_matches: List[MatchRef] = pro_quo.compare(source_file_content, target_file_content, quid_matches_all,
                                                    source_text_parallel_print, parallel_print_first_page,
                                                    parallel_print_last_page)
    all_matches = short_matches

    if len(quid_matches_long) > 0:
        all_matches.extend(quid_matches_long)
        all_matches = Helper.remove_overlapping_matches(all_matches, target_file_content)
        all_matches.sort(key=lambda x: x.target_span.start, reverse=False)

    if not export_text:
        for match in all_matches:
            match.source_span.text = ''
            match.target_span.text = ''

    if not export_ref:
        for match in all_matches:
            match.reference = None

    if output_type == 'json':
        result = json.dumps(all_matches, default=__json_encoder_proquo)
        file_ending = 'json'
    elif output_type == 'csv':
        result = f'sstart{csv_sep}send{csv_sep}tstart{csv_sep}tend{csv_sep}stext{csv_sep}ttext'

        if export_ref:
            result += f'{csv_sep}rstart{csv_sep}rend{csv_sep}rtext'

        for match in all_matches:
            source_span = match.source_span
            target_span = match.target_span

            result += f'\n{source_span.start}{csv_sep}{source_span.end}' \
                      f'{csv_sep}{target_span.start}{csv_sep}{target_span.end}'

            if export_text:
                source_span_text = re.sub(rf'[{csv_sep}\n]', ' ', source_span.text)
                target_span_text = re.sub(rf'[{csv_sep}\n]', ' ', target_span.text)
                result += f'{csv_sep}{source_span_text}{csv_sep}{target_span_text}'

            if export_ref and match.reference:
                ref_text = re.sub(rf'[{csv_sep}\n]', ' ', match.reference.text)
                result += f'{csv_sep}{match.reference.start}{csv_sep}{match.reference.end}{csv_sep}{ref_text}'
            elif export_ref:
                result += f'{csv_sep}{csv_sep}{csv_sep}'

        file_ending = 'csv'
    else:
        result = ''

        for match in all_matches:
            result += f'\n{match.source_span.start}\t{match.source_span.end}' \
                      f'\t{match.target_span.start}\t{match.target_span.end}'

            if export_text:
                result += f'\t{match.source_span.text}\t{match.target_span.text}'

            if export_ref and match.reference:
                result += f'\t{match.reference.start}\t{match.reference.end}\t{match.reference.text}'

        result = result.strip()
        file_ending = 'txt'

    if output_folder_path:
        filename = f'{filename}.{file_ending}'

        with open(join(output_folder_path, filename), 'w', encoding='utf-8') as output_file:
            output_file.write(result)
    else:
        print('Results:')
        print(result)


def __train_reference(train_file_path, val_file_path, output_path):
    TrainReference.train(train_file_path, val_file_path, output_path)


def __train_relation(train_file_path, val_file_path, output_path, arch_type):
    if arch_type == 'bert':
        TrainRelationBert.train(train_file_path, val_file_path, output_path)
    elif arch_type == 'lstm':
        TrainRelationLstm.train(train_file_path, val_file_path, output_path)


def __test_reference(test_file_path, vocab_file_path, model_file_path):
    TestReference.test(test_file_path, vocab_file_path, model_file_path)


def __test_relation_lstm(test_file_path, vocab_file_path, model_file_path):
    TestRelationLstm.test(test_file_path, vocab_file_path, model_file_path)


def __test_relation_bert(test_file_path, tokenizer_folder_path, model_folder_path):
    TestRelationBert.test(test_file_path, tokenizer_folder_path, model_folder_path)


def __run_compare(source_file_path, target_path, ref_vocab_file_path, ref_model_file_path, rel_tokenizer_folder_path,
                  rel_model_folder_path, output_folder_path, parallel_print_files,
                  parallel_print_first_page, parallel_print_last_page, export_text, export_ref, output_type, csv_sep,
                  open_quote, close_quote, include_long_matches_in_result, max_num_processes):

    reference_vectorizer = ReferenceVectorizer.from_vocab_file(ref_vocab_file_path, 25, True)
    reference_model_trainer = ReferenceModelTrainer(25, True, 32, 32, 0.2, 512, 10)
    reference_model = reference_model_trainer.get_model(reference_vectorizer.max_id)
    reference_model.load_weights(ref_model_file_path)

    relation_vectorizer = RelationVectorizerBert.from_saved(200, rel_tokenizer_folder_path, True)
    relation_model = transformers.TFBertForSequenceClassification.from_pretrained(rel_model_folder_path, num_labels=2)

    with open(source_file_path, 'r', encoding='utf-8') as source_file:
        source_file_content = source_file.read().lower()

    pro_quo = ProQuo(reference_model, reference_vectorizer, relation_model, relation_vectorizer, open_quote,
                     close_quote)

    if isfile(target_path) and target_path.endswith('.txt'):
        with open(target_path, 'r', encoding='utf-8') as target_file:
            target_file_content = target_file.read()

        filename = splitext(basename(target_path))[0]

        quid_all = Quid(min_match_length=2, keep_ambiguous_matches=True)
        quid_matches_all = quid_all.compare(source_file_content, target_file_content)

        quid_matches_long = []
        if include_long_matches_in_result:
            quid_long = Quid(min_match_length=5, keep_ambiguous_matches=False)
            quid_matches_long = quid_long.compare(source_file_content, target_file_content)

        source_text_parallel_print = False

        if filename in parallel_print_files:
            source_text_parallel_print = True

        __process_file(pro_quo, filename, source_file_content, target_file_content, quid_matches_all, quid_matches_long,
                       output_folder_path, source_text_parallel_print, parallel_print_first_page,
                       parallel_print_last_page, export_text, export_ref, output_type, csv_sep)
    elif isdir(target_path):
        quid_matches_all_per_file = get_quid_matches_mp(source_file_content, target_path, max_num_processes, 2, True)

        quid_matches_long_per_file = None
        if include_long_matches_in_result:
            quid_matches_long_per_file = get_quid_matches_mp(source_file_content, target_path, max_num_processes, 5,
                                                             False)

        file_pos = 0
        for fileOrFolder in listdir(target_path):
            target_file_path = join(target_path, fileOrFolder)

            if isfile(target_file_path) and target_file_path.endswith('.txt'):
                filename = splitext(basename(target_file_path))[0]

                with open(target_file_path, 'r', encoding='utf-8') as target_file:
                    target_file_content = target_file.read()

                quid_matches_all = quid_matches_all_per_file[file_pos]

                quid_matches_long = []
                if quid_matches_long_per_file:
                    quid_matches_long = quid_matches_long_per_file[file_pos]

                source_text_parallel_print = False

                if filename in parallel_print_files:
                    source_text_parallel_print = True

                __process_file(pro_quo, filename, source_file_content, target_file_content, quid_matches_all,
                               quid_matches_long, output_folder_path, source_text_parallel_print,
                               parallel_print_first_page, parallel_print_last_page, export_text, export_ref,
                               output_type, csv_sep)

                file_pos += 1


def main(argv=None):
    proquo_description = 'ProQuo is a tool for the detection of short quotations (<= 4 words) between two texts, a' \
                         ' source text and a target text. The target text is the text quoting the source text.' \
                         ' Quotations in the target text need to be clearly marked with quotations marks.'
    train_description = 'ProQuo train allows the user to train their own models.'
    train_reference_description = 'ProQuo train reference allows the user to train their own reference model.'
    train_relation_description = 'ProQuo train relation allows the user to train their own relation model.'
    test_description = 'ProQuo test allows the user to test their trained models.'
    test_reference_description = 'ProQuo test reference allows the user to test their trained reference model.'
    test_relation_description = 'ProQuo test relation allows the user to test their trained relation model.'
    test_relation_lstm_description = 'ProQuo test relation lstm allows the user to test their trained lstm relation' \
                                     ' model.'
    test_relation_bert_description = 'ProQuo test relation lstm allows the user to test their trained bert relation' \
                                     ' model.'

    compare_description = 'ProQuo compare allows the user to find short quotations (<= 4 words) in two texts, a' \
                          ' source text and a target text. The target text is the text quoting the source text.' \
                          ' Quotations in the target text need to be clearly marked with quotations marks.'

    argument_parser = ArgumentParser(prog='proquo', description=proquo_description)

    subparsers_command = argument_parser.add_subparsers(dest='command')
    subparsers_command.required = True

    parser_train = subparsers_command.add_parser('train', help=train_description, description=train_description)
    subparsers_train_model = parser_train.add_subparsers(dest='train_model')
    subparsers_train_model.required = True

    parser_train_reference = subparsers_train_model.add_parser('reference', help=train_reference_description,
                                                               description=train_reference_description)

    parser_train_reference.add_argument('train_file_path', nargs=1, metavar='train-file-path',
                                        help='Path to the txt file containing the training examples')
    parser_train_reference.add_argument('val_file_path', nargs=1, metavar='val-file-path',
                                        help='Path to the txt file containing the validation examples')
    parser_train_reference.add_argument('output_folder_path', nargs=1, metavar='output-folder_path',
                                        help='Path to the folder for storing the output model and vocabulary')
    parser_train_reference.add_argument('--create-dated-subfolder', dest='create_dated_subfolder', default=False,
                                        action='store_true',
                                        help='Create a subfolder named with the current date to store the results')
    parser_train_reference.add_argument('--no-create-dated-subfolder', dest='create_dated_subfolder',
                                        action='store_false',
                                        help='Do not create a subfolder named with the current date to store the '
                                             'results')

    parser_train_relation = subparsers_train_model.add_parser('relation', help=train_relation_description,
                                                              description=train_relation_description)

    parser_train_relation.add_argument('train_file_path', nargs=1, metavar='train-file-path',
                                       help='Path to the txt file containing the training examples')
    parser_train_relation.add_argument('val_file_path', nargs=1, metavar='val-file-path',
                                       help='Path to the txt file containing the validation examples')
    parser_train_relation.add_argument('output_folder_path', nargs=1, metavar='output-folder-path',
                                       help='Path to the folder for storing the output model and vocabulary')
    parser_train_relation.add_argument('--create-dated-subfolder', dest='create_dated_subfolder', default=False,
                                       action='store_true',
                                       help='Create a subfolder named with the current date to store the results')
    parser_train_relation.add_argument('--no-create-dated-subfolder', dest='create_dated_subfolder',
                                       action='store_false',
                                       help='Do not create a subfolder named with the current date to store the '
                                            'results')
    parser_train_relation.add_argument('--arch', choices=['lstm', 'bert'], dest='arch_type', default='bert',
                                       help='The model architecture to train')

    parser_test = subparsers_command.add_parser('test', help=test_description, description=test_description)
    subparsers_test_model = parser_test.add_subparsers(dest='test_model')
    subparsers_test_model.required = True

    parser_test_reference = subparsers_test_model.add_parser('reference', help=test_reference_description,
                                                             description=test_reference_description)

    parser_test_reference.add_argument('test_file_path', nargs=1, metavar='test-file-path',
                                       help='Path to the txt file containing the testing examples')
    parser_test_reference.add_argument('vocab_file_path', nargs=1, metavar='vocab-file-path',
                                       help='Path to the vocab file')
    parser_test_reference.add_argument('model_file_path', nargs=1, metavar='model-file-path',
                                       help='Path to the model file')

    parser_test_relation = subparsers_test_model.add_parser('relation', help=test_relation_description,
                                                            description=test_relation_description)

    subparsers_test_relation_arch = parser_test_relation.add_subparsers(dest='test_model_relation_arch')
    subparsers_test_relation_arch.required = True

    parser_test_relation_lstm = subparsers_test_relation_arch.add_parser('lstm', help=test_relation_lstm_description,
                                                                         description=test_relation_lstm_description)

    parser_test_relation_lstm.add_argument('test_file_path', nargs=1, metavar='test-file-path',
                                           help='Path to the txt file containing the testing examples')
    parser_test_relation_lstm.add_argument('vocab_file_path', nargs=1, metavar='vocab-file-path',
                                           help='Path to the vocab file')
    parser_test_relation_lstm.add_argument('model_file_path', nargs=1, metavar='model-file-path',
                                           help='Path to the model file')

    parser_test_relation_bert = subparsers_test_relation_arch.add_parser('bert', help=test_relation_bert_description,
                                                                         description=test_relation_bert_description)

    parser_test_relation_bert.add_argument('test_file_path', nargs=1, metavar='test-file-path',
                                           help='Path to the txt file containing the testing examples')
    parser_test_relation_bert.add_argument('tokenizer_folder_path', nargs=1, metavar='tokenizer-folder-path',
                                           help='Path to the vocab file')
    parser_test_relation_bert.add_argument('model_folder_path', nargs=1, metavar='model-folder-path',
                                           help='Path to the model file')

    parser_compare = subparsers_command.add_parser('compare', help=compare_description, description=compare_description)

    parser_compare.add_argument('source_file_path', nargs=1, metavar='source-file-path',
                                help='Path to the source text file')
    parser_compare.add_argument('target_path', nargs=1, metavar='target-path',
                                help='Path to the target text file or folder')
    parser_compare.add_argument('ref_vocab_file_path', nargs=1, metavar='ref-vocab-file-path',
                                help='Path to the reference vocab text file')
    parser_compare.add_argument('ref_model_file_path', nargs=1, metavar='ref-model-file-path',
                                help='Path to the reference model file')
    parser_compare.add_argument('rel_tokenizer_folder_path', nargs=1, metavar='rel-tokenizer-folder-path',
                                help='Path to the relation tokenizer folder')
    parser_compare.add_argument('rel_model_folder_path', nargs=1, metavar='rel-model-folder-path',
                                help='Path to the relation model folder')
    parser_compare.add_argument('--quid-match-path', dest='quid_match_path',
                                help='Path to the file or folder with quid matches. If this option is not set, then'
                                     ' Quid is used to find long matches.')
    parser_compare.add_argument('--output-folder-path', dest='output_folder_path',
                                help='The output folder path. If this option is set the output will be saved to a file'
                                     ' created in the specified folder')
    parser_compare.add_argument('--create-dated-subfolder', dest='create_dated_subfolder', default=False,
                                action='store_true',
                                help='Create a subfolder named with the current date to store the results')
    parser_compare.add_argument('--no-create-dated-subfolder', dest='create_dated_subfolder',
                                action='store_false',
                                help='Do not create a subfolder named with the current date to store the results')
    parser_compare.add_argument('--parallel-print-files', dest='parallel_print_files', nargs='*', default=[],
                                help='Filenames of files which quote a parallel print edition')
    parser_compare.add_argument('--parallel-print-first-page', dest='parallel_print_first_page', default=0,
                                help='Number of the first page with parallel print')
    parser_compare.add_argument('--parallel-print-last-page', dest='parallel_print_last_page', default=0,
                                help='Number of the last page with parallel print')
    parser_compare.add_argument('--text', dest='export_text', default=True, action='store_true',
                                help='Include matched text in the returned data structure')
    parser_compare.add_argument('--no-text', dest='export_text', action='store_false',
                                help='Do not include matched text in the returned data structure')
    parser_compare.add_argument('--ref', dest='export_ref', default=False, action='store_true',
                                help='Include matched reference in the returned data structure')
    parser_compare.add_argument('--no-ref', dest='export_ref', action='store_false',
                                help='Do not include matched reference in the returned data structure')
    parser_compare.add_argument('--output-type', choices=['json', 'text', 'csv'], dest='output_type', default='json',
                                help='The output type')
    parser_compare.add_argument('--csv-sep', dest='csv_sep', type=str, help='output separator for csv'
                                                                            ' (default: \'\\t\')', default='\t')
    parser_compare.add_argument('--open-quote', dest='open_quote', type=str,
                                help='The quotation open character. If this option is not set, then the type of'
                                     ' quotation marks used in a target text is auto automatically identified.')
    parser_compare.add_argument('--close-quote', dest='close_quote', type=str,
                                help='The quotation close character. If this option is not set, then the type of'
                                     ' quotation marks used in a target text is auto automatically identified.')
    parser_compare.add_argument('--include-long-matches-in-result', dest='include_long_matches_in_result',
                                default=False, action='store_true', help='Include matches longer than 4 words in the'
                                                                         ' output')
    parser_compare.add_argument('--max-num-processes', dest="max_num_processes", action=OptionValueCheckAction,
                                default=1, type=int, help="Maximum number of processes to use for parallel processing."
                                                          "This can significantly speed up the process.")

    args = argument_parser.parse_args(argv)

    if args.command == 'train':
        if args.train_model == 'reference':
            train_file_path = args.train_file_path[0]
            val_file_path = args.val_file_path[0]
            output_folder_path = args.output_folder_path[0]
            create_dated_subfolder = args.create_dated_subfolder

            if output_folder_path:
                if not exists(output_folder_path):
                    raise Exception(f'{output_folder_path} does not exist!')

            if create_dated_subfolder:
                now = datetime.now()
                date_time_string = now.strftime('%Y_%m_%d_%H_%M_%S')
                output_folder_path = join(output_folder_path, date_time_string)
                Path(output_folder_path).mkdir(parents=True, exist_ok=True)

            __train_reference(train_file_path, val_file_path, output_folder_path)

        elif args.train_model == 'relation':
            train_file_path = args.train_file_path[0]
            val_file_path = args.val_file_path[0]
            output_folder_path = args.output_folder_path[0]
            create_dated_subfolder = args.create_dated_subfolder
            arch_type = args.arch_type

            if create_dated_subfolder:
                now = datetime.now()
                date_time_string = now.strftime('%Y_%m_%d_%H_%M_%S')
                output_folder_path = join(output_folder_path, date_time_string)
                Path(output_folder_path).mkdir(parents=True, exist_ok=True)

            __train_relation(train_file_path, val_file_path, output_folder_path, arch_type)

    elif args.command == 'test':
        if args.test_model == 'reference':
            test_file_path = args.test_file_path[0]
            vocab_file_path = args.vocab_file_path[0]
            model_file_path = args.model_file_path[0]
            __test_reference(test_file_path, vocab_file_path, model_file_path)

        elif args.test_model == 'relation':
            if args.test_model_relation_arch == 'lstm':
                test_file_path = args.test_file_path[0]
                vocab_file_path = args.vocab_file_path[0]
                model_file_path = args.model_file_path[0]
                __test_relation_lstm(test_file_path, vocab_file_path, model_file_path)

            elif args.test_model_relation_arch == 'bert':
                test_file_path = args.test_file_path[0]
                tokenizer_folder_path = args.tokenizer_folder_path[0]
                model_folder_path = args.model_folder_path[0]
                __test_relation_bert(test_file_path, tokenizer_folder_path, model_folder_path)

    elif args.command == 'compare':
        source_file_path = args.source_file_path[0]
        target_path = args.target_path[0]
        ref_vocab_file_path = args.ref_vocab_file_path[0]
        ref_model_file_path = args.ref_model_file_path[0]
        rel_tokenizer_folder_path = args.rel_tokenizer_folder_path[0]
        rel_model_folder_path = args.rel_model_folder_path[0]
        output_folder_path = args.output_folder_path
        create_dated_subfolder = args.create_dated_subfolder
        parallel_print_files = args.parallel_print_files
        parallel_print_first_page = args.parallel_print_first_page
        parallel_print_last_page = args.parallel_print_last_page
        export_text = args.export_text
        export_ref = args.export_ref
        output_type = args.output_type
        csv_sep = bytes(args.csv_sep, 'utf-8').decode('unicode_escape')
        open_quote = args.open_quote
        close_quote = args.close_quote
        include_long_matches_in_result = args.include_long_matches_in_result
        max_num_processes = args.max_num_processes

        if create_dated_subfolder:
            now = datetime.now()
            date_time_string = now.strftime('%Y_%m_%d_%H_%M_%S')
            output_folder_path = join(output_folder_path, date_time_string)
            Path(output_folder_path).mkdir(parents=True, exist_ok=True)

        __run_compare(source_file_path, target_path, ref_vocab_file_path, ref_model_file_path,
                      rel_tokenizer_folder_path, rel_model_folder_path, output_folder_path,
                      parallel_print_files, parallel_print_first_page, parallel_print_last_page, export_text,
                      export_ref, output_type, csv_sep, open_quote, close_quote, include_long_matches_in_result,
                      max_num_processes)


if __name__ == '__main__':
    sys.exit(main())
