import os
from colorama import Fore

from polyglot.deepl_request import DeeplRequest
from polyglot.managers import TextManager, JSONManager, POManager, DocumentManager, Manager

from polyglot.arguments import Arguments

DOCUMENTS_SUPPORTED_BY_DEEPL: list = [
    '.docx',
    '.pptx',
    '.html',
    '.htm'
]


def execute_command(arguments: Arguments):

    if not arguments.action:
        print(f"{Fore.RED}No action selected.")
        os._exit(0)

    deepl: DeeplRequest = DeeplRequest(arguments.target_lang, arguments.source_lang)

    if arguments.action == 'translate':

        name, extension = os.path.splitext(arguments.source_file)

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            manager: Manager = DocumentManager(deepl, arguments.source_file,
                                               arguments.output_directory)
        elif extension == '.json':
            manager: Manager = JSONManager(deepl, arguments.source_file,
                                           arguments.output_directory)
        elif extension == '.po':
            manager: Manager = POManager(
                deepl, arguments.source_file, arguments.output_directory)
        else:
            manager: Manager = TextManager(
                deepl, arguments.source_file, arguments.output_directory)

        manager.translate_source_file()

        print('\nFinish.\n')

    elif arguments.action == 'set_key':
        deepl.set_key()

    elif arguments.action == 'print_supported_languages':
        deepl.print_supported_languages()

    elif arguments.action == 'print_usage_info':
        deepl.print_usage_info()