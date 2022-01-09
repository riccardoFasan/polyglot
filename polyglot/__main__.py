#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from colorama import init, Fore

from polyglot.deepl_request import DeeplRequest
from polyglot.managers import TextManager, JSONManager, POManager, DocumentManager

init(autoreset=True)

DOCUMENTS_SUPPORTED_BY_DEEPL: list = [
    '.docx',
    '.pptx',
    '.html',
    '.htm'
]


def translate_or_print_data():

    parser: ArgumentParser = get_parser()
    args: dict = parser.parse_args()

    if not args.action:
        print(f"{Fore.RED}No action selected.")
        os._exit(0)

    deepl: DeeplRequest = DeeplRequest(args.target_lang, args.source_lang)

    if args.action == 'translate':

        if args.source_file is None or args.target_lang is None:
            parser.error("translate requires --source_file and --target_lang.")

        name, extension = os.path.splitext(args.source_file)

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            manager: DocumentManager = DocumentManager(deepl, args.source_file,
                                                       args.output_directory)
        elif extension == '.json':
            manager: JSONManager = JSONManager(deepl, args.source_file,
                                               args.output_directory)
        elif extension == '.po':
            manager: POManager = POManager(
                deepl, args.source_file, args.output_directory)
        else:
            manager: TextManager = TextManager(
                deepl, args.source_file, args.output_directory)

        manager.translate_source_file()

        print('\nFinish.\n')

    elif args.action == 'set_key':
        deepl.set_key()

    elif args.action == 'print_supported_languages':
        deepl.print_supported_languages()

    elif args.action == 'print_usage_info':
        deepl.print_usage_info()


def get_parser():
    actions: list[str] = ['translate', 'set_key',
                          'print_supported_languages', 'print_usage_info']
    parser: ArgumentParser = ArgumentParser(
        description='Using the DeepL API, this script translate the given file.')
    parser.add_argument(
        'action', type=str, help="The action that will be exectued. The following options are for the translate command.", choices=actions)
    parser.add_argument('-p', '--source_file', type=str,
                        help='The file to be translated. Required if the action is "translate."', default=None)
    parser.add_argument('-t', '--target_lang', type=str,
                        help='the code of the language into which you want to translate the source file. Required if the action is "translate".', default=None)
    parser.add_argument('-o', '--output_directory', type=str,
                        help='The directory where the output file will be located. Will be used the working directory if this option is invalid or not used.', default=None)
    parser.add_argument('-s', '--source_lang', type=str,
                        help='Source file language code. Detected automatically by DeepL by default. Specifying it can increase performance and make translations more accurate.', default=None)
    return parser


if __name__ == '__main__':
    try:
        translate_or_print_data()
    except KeyboardInterrupt:
        print('\n\nInterrupted by user.')
