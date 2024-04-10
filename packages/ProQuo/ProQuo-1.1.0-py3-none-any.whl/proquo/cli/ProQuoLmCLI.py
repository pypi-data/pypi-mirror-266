from argparse import ArgumentParser, BooleanOptionalAction
import sys
import logging
from os.path import join, isfile, splitext, basename, isdir, exists
from os import listdir
from datetime import datetime
from pathlib import Path
from typing import List

from quid.core.Quid import Quid
from quid.match.Match import Match
from quid.match.MatchSpan import MatchSpan

from proquo.cli.OptionValueCheckAction import OptionValueCheckAction
from proquo.core import Helper
from proquo.match.MatchRef import MatchRef
from proquo.core.ProQuoLm import ProQuoLm
from proquo.model.linking.LinkingVectorizer import LinkingVectorizer
import transformers

from proquo.testing.linking import TestLinking
from proquo.training.linking import TrainLinking

import re
import json

from proquo.cli.Helper import get_quid_matches_mp


def __json_encoder_proquo(obj):
    if isinstance(obj, MatchRef):
        result_dict = obj.__dict__
        del result_dict['reference']
        return result_dict

    if isinstance(obj, MatchSpan):
        result_dict = obj.__dict__

        if not result_dict['text']:
            del result_dict['text']

        return result_dict

    return obj.__dict__


def __process_file(pro_quo_lm, filename, source_file_content, target_file_content, quid_matches_all, quid_matches_long,
                   output_folder_path, export_text, output_type, csv_sep):
    logging.info(f'Processing {filename}')
    short_matches: List[MatchRef] = pro_quo_lm.compare(source_file_content, target_file_content, quid_matches_all)
    all_matches: List[Match] = short_matches

    if len(quid_matches_long) > 0:
        all_matches.extend(quid_matches_long)
        all_matches = Helper.remove_overlapping_matches(all_matches, target_file_content)
        all_matches.sort(key=lambda x: x.target_span.start, reverse=False)

    if not export_text:
        for match in all_matches:
            match.source_span.text = ''
            match.target_span.text = ''

    if output_type == 'json':
        result = json.dumps(all_matches, default=__json_encoder_proquo)
        file_ending = 'json'
    elif output_type == 'csv':
        result = f'sstart{csv_sep}send{csv_sep}tstart{csv_sep}tend{csv_sep}stext{csv_sep}ttext'

        for match in all_matches:
            source_span = match.source_span
            target_span = match.target_span

            result += f'\n{source_span.start}{csv_sep}{source_span.end}' \
                      f'{csv_sep}{target_span.start}{csv_sep}{target_span.end}'

            if export_text:
                source_span_text = re.sub(rf'[{csv_sep}\n]', ' ', source_span.text)
                target_span_text = re.sub(rf'[{csv_sep}\n]', ' ', target_span.text)
                result += f'{csv_sep}{source_span_text}{csv_sep}{target_span_text}'

        file_ending = 'csv'
    else:
        result = ''

        for match in all_matches:
            result += f'\n{match.source_span.start}\t{match.source_span.end}' \
                      f'\t{match.target_span.start}\t{match.target_span.end}'

            if export_text:
                result += f'\t{match.source_span.text}\t{match.target_span.text}'

        result = result.strip()
        file_ending = 'txt'

    if output_folder_path:
        filename = f'{filename}.{file_ending}'

        with open(join(output_folder_path, filename), 'w', encoding='utf-8') as output_file:
            output_file.write(result)
    else:
        print('Results:')
        print(result)


def __train(train_file_path, val_file_path, batch_size, num_epochs, lower_case, model_name, output_folder_path):
    TrainLinking.train(train_file_path, val_file_path, batch_size, num_epochs, lower_case, model_name,
                       output_folder_path)


def __test(test_file_path, tokenizer_folder_path, model_folder_path, lower_case):
    TestLinking.test(test_file_path, tokenizer_folder_path, model_folder_path, lower_case)


def __run_compare(source_file_path, target_path, tokenizer_folder_path, model_folder_path, lower_case,
                  output_folder_path, export_text, output_type, csv_sep, open_quote, close_quote,
                  include_long_matches_in_result, max_num_processes):
    link_vectorizer = LinkingVectorizer.from_saved(512, tokenizer_folder_path, lower_case)
    link_model = transformers.TFBertForSequenceClassification.from_pretrained(model_folder_path, num_labels=2)

    with open(source_file_path, 'r', encoding='utf-8') as source_file:
        source_file_content = source_file.read()

    pro_quo_lm = ProQuoLm(link_model, link_vectorizer, open_quote, close_quote)

    if isfile(target_path) and target_path.endswith('.txt'):
        with open(target_path, 'r', encoding='utf-8') as target_file:
            target_file_content = target_file.read()

        filename = splitext(basename(target_path))[0]

        logging.info(f'Running Quid for {filename} to get all matches')

        quid_all = Quid(min_match_length=2, keep_ambiguous_matches=True)
        quid_matches_all = quid_all.compare(source_file_content, target_file_content)

        quid_matches_long = []
        if include_long_matches_in_result:
            logging.info(f'Running Quid for {filename} to get long matches')
            quid_long = Quid(min_match_length=5, keep_ambiguous_matches=False)
            quid_matches_long = quid_long.compare(source_file_content, target_file_content)

        __process_file(pro_quo_lm, filename, source_file_content, target_file_content, quid_matches_all,
                       quid_matches_long, output_folder_path, export_text, output_type, csv_sep)
    elif isdir(target_path):
        logging.info(f'Running Quid for all files to get all matches')
        quid_matches_all_per_file = get_quid_matches_mp(source_file_content, target_path, max_num_processes, 2, True)

        quid_matches_long_per_file = None
        if include_long_matches_in_result:
            logging.info(f'Running Quid for all files to get long matches')
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

                __process_file(pro_quo_lm, filename, source_file_content, target_file_content, quid_matches_all,
                               quid_matches_long, output_folder_path, export_text, output_type, csv_sep)

                file_pos += 1


def main(argv=None):
    train_description = 'ProQuoLm train allows the user to train their own models.'
    test_description = 'ProQuoLm test allows the user to test their trained model.'
    compare_description = 'ProQuoLm compare allows the user to find short quotations (<= 4 words) in two texts, a' \
                          ' source text and a target text. The target text is the text quoting the source text.' \
                          ' Quotations in the target text need to be clearly marked with quotations marks.'

    argument_parser = ArgumentParser(prog='proquolm', description='ProQuoLm is a tool to find short quotations'
                                                                  '(<= 4 words) in texts.')

    argument_parser.add_argument('--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                                                           'CRITICAL'],
                                 help='Set the logging level', default='WARNING')

    subparsers_command = argument_parser.add_subparsers(dest='command')
    subparsers_command.required = True

    parser_train = subparsers_command.add_parser('train', help=train_description, description=train_description)

    parser_train.add_argument('train_file_path', nargs=1, metavar='train-file-path',
                              help='Path to the txt file containing the training examples')
    parser_train.add_argument('val_file_path', nargs=1, metavar='val-file-path',
                              help='Path to the txt file containing the validation examples')
    parser_train.add_argument('output_folder_path', nargs=1, metavar='output-folder_path',
                              help='Path to the folder for storing the output model and vocabulary')
    parser_train.add_argument('--create-dated-subfolder', dest='create_dated_subfolder', default=False,
                              action=BooleanOptionalAction,
                              help='Create a subfolder named with the current date to store the results')
    parser_train.add_argument('--base-model-name', dest="base_model_name",
                              default="bert-base-german-dbmdz-uncased", help="The model name")
    parser_train.add_argument('--lower-case', dest="lower_case", default=True, action=BooleanOptionalAction,
                              help="Train model on lower case text")
    parser_train.add_argument('--batch-size', dest="batch_size", default=4, type=int, help="The batch size")
    parser_train.add_argument('--num-epochs', dest="num_epochs", default=3, type=int,
                              help="The number of epochs to train for")

    parser_test = subparsers_command.add_parser('test', help=test_description, description=test_description)

    parser_test.add_argument('test_file_path', nargs=1, metavar='test-file-path',
                             help='Path to the txt file containing the testing examples')
    parser_test.add_argument('tokenizer_folder_path', nargs=1, metavar='tokenizer-folder-path',
                             help='Path to the vocab file')
    parser_test.add_argument('model_folder_path', nargs=1, metavar='model-folder-path',
                             help='Path to the model file')
    parser_test.add_argument('--lower-case', dest="lower_case", default=True, action=BooleanOptionalAction,
                             help="Test model on lower case text")

    parser_compare = subparsers_command.add_parser('compare', help=compare_description, description=compare_description)

    parser_compare.add_argument('source_file_path', nargs=1, metavar='source-file-path',
                                help='Path to the source text file')
    parser_compare.add_argument('target_path', nargs=1, metavar='target-path',
                                help='Path to the target text file or folder')
    parser_compare.add_argument('--tokenizer', dest='tokenizer', default='fredr0id/proquolm',
                                help='Name of the tokenizer to load from Hugging Face or path to the tokenizer folder')
    parser_compare.add_argument('--model', dest='model', default='fredr0id/proquolm',
                                help='Name of the model to load from Hugging Face or path to the model folder')
    parser_compare.add_argument('--lower-case', dest="lower_case", default=True, action=BooleanOptionalAction,
                                help="Run model inference on lower case text")
    parser_compare.add_argument('--output-folder-path', dest='output_folder_path',
                                help='The output folder path. If this option is set the output will be saved to a file'
                                     ' created in the specified folder')
    parser_compare.add_argument('--create-dated-subfolder', dest='create_dated_subfolder', default=False,
                                action=BooleanOptionalAction,
                                help='Create a subfolder named with the current date to store the results')
    parser_compare.add_argument('--text', dest='export_text', default=True, action=BooleanOptionalAction,
                                help='Include matched text in the returned data structure')
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
    parser_compare.add_argument('--max-num-processes', dest='max_num_processes', action=OptionValueCheckAction,
                                default=1, type=int, help='Maximum number of processes to use for parallel processing.'
                                                          ' This can significantly speed up the process.')

    args = argument_parser.parse_args(argv)

    log_level = args.log_level
    logging.getLogger().setLevel(logging.getLevelName(log_level))

    if args.command == 'train':
        train_file_path = args.train_file_path[0]
        val_file_path = args.val_file_path[0]
        output_folder_path = args.output_folder_path[0]
        create_dated_subfolder = args.create_dated_subfolder
        base_model_name = args.base_model_name
        lower_case = args.lower_case
        num_epochs = args.num_epochs
        batch_size = args.batch_size

        if output_folder_path:
            if not exists(output_folder_path):
                raise Exception(f'{output_folder_path} does not exist!')

        if create_dated_subfolder:
            now = datetime.now()
            date_time_string = now.strftime('%Y_%m_%d_%H_%M_%S')
            output_folder_path = join(output_folder_path, date_time_string)
            Path(output_folder_path).mkdir(parents=True, exist_ok=True)

        __train(train_file_path, val_file_path, batch_size, num_epochs, lower_case, base_model_name, output_folder_path)

    elif args.command == 'test':
        test_file_path = args.test_file_path[0]
        tokenizer_folder_path = args.tokenizer_folder_path[0]
        model_folder_path = args.model_folder_path[0]
        lower_case = args.lower_case
        __test(test_file_path, tokenizer_folder_path, model_folder_path, lower_case)

    elif args.command == 'compare':
        source_file_path = args.source_file_path[0]
        target_path = args.target_path[0]
        tokenizer_name_or_path = args.tokenizer
        model_name_or_path = args.model
        lower_case = args.lower_case
        output_folder_path = args.output_folder_path
        create_dated_subfolder = args.create_dated_subfolder
        export_text = args.export_text
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

        __run_compare(source_file_path, target_path, tokenizer_name_or_path, model_name_or_path, lower_case,
                      output_folder_path, export_text, output_type, csv_sep, open_quote, close_quote,
                      include_long_matches_in_result, max_num_processes)


if __name__ == '__main__':
    sys.exit(main())
