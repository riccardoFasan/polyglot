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


class Translator():
    __options: arguments.Arguments
    __deepl: deepl_request.DeeplRequest

    def __init__(self, arguments: arguments.Arguments):
        colorama.init(autoreset=True)
        self.__options = arguments
        self.__deepl = deepl_request.DeeplRequest(
            target_lang=self.__options.target_lang,
            source_lang=self.__options.source_lang
        )

    def execute_command(self):

        if not self.__options.action:
            print(f"{colorama.Fore.RED}No action selected.")
            os._exit(0)

        if self.__options.action == 'translate':
            manager: managers.Manager = self.__get_manager()
            manager.translate_source_file()
            print('\nFinish.\n')

        elif self.__options.action == 'set_key':
            self.__deepl.set_key()

        elif self.__options.action == 'print_supported_languages':
            self.__deepl.print_supported_languages()

        elif self.__options.action == 'print_usage_info':
            self.__deepl.print_usage_info()

    def __get_manager(self) -> managers.Manager:

        name, extension = os.path.splitext(self.__options.source_file)

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            return managers.DocumentManager(self.__deepl, self.__options.source_file, self.__options.output_directory)
        if extension == '.json':
            return managers.JSONManager(self.__deepl, self.__options.source_file, self.__options.output_directory)
        if extension == '.po':
            return managers.POManager(self.__deepl, self.__options.source_file, self.__options.output_directory)
        return managers.TextManager(self.__deepl, self.__options.source_file, self.__options.output_directory)
