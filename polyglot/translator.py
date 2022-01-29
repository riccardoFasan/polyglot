import os

import colorama

from polyglot import managers
from polyglot import deepl_request
from polyglot import arguments

DOCUMENTS_SUPPORTED_BY_DEEPL: list[str] = [
    '.docx',
    '.pptx',
    '.html',
    '.htm'
]


def execute_command(arguments: arguments.Arguments):

    colorama.init(autoreset=True)

    if not arguments.action:
        print(f"{colorama.Fore.RED}No action selected.")
        os._exit(0)

    deepl: deepl_request.DeeplRequest = deepl_request.DeeplRequest(
        arguments.target_lang, arguments.source_lang)

    if arguments.action == 'translate':
        manager: managers.Manager = get_manager(deepl, arguments)
        manager.translate_source_file()
        print('\nFinish.\n')

    elif arguments.action == 'set_key':
        deepl.set_key()

    elif arguments.action == 'print_supported_languages':
        deepl.print_supported_languages()

    elif arguments.action == 'print_usage_info':
        deepl.print_usage_info()


def get_manager(deepl: deepl_request.DeeplRequest, arguments: arguments.Arguments) -> managers.Manager:

    name, extension = os.path.splitext(arguments.source_file)

    if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
        return managers.DocumentManager(deepl, arguments.source_file, arguments.output_directory)
    if extension == '.json':
        return managers.JSONManager(deepl, arguments.source_file, arguments.output_directory)
    if extension == '.po':
        return managers.POManager(deepl, arguments.source_file, arguments.output_directory)
    return managers.TextManager(deepl, arguments.source_file, arguments.output_directory)
