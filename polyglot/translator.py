import os
import colorama
from polyglot import deepl, managers, arguments

DOCUMENTS_SUPPORTED_BY_DEEPL: list[str] = [
    '.docx',
    '.pptx',
    '.html',
    '.htm'
]


class Translator():
    __options: arguments.Arguments
    __requester: deepl.Requester
    __license_manager: deepl.LicenseManager

    def __init__(self, arguments: arguments.Arguments):
        colorama.init(autoreset=True)
        self.__options = arguments

    def execute_command(self):

        if self.__options.action == 'set_license':
            self.__license_manager: deepl.LicenseManager = deepl.LicenseManager()
            self.__license_manager.set_license()

        else:
            self.__requester = deepl.Requester(
                target_lang=self.__options.target_lang,
                source_lang=self.__options.source_lang
            )

        if self.__options.action == 'translate':
            manager: managers.Manager = self.__get_manager()
            manager.translate_source_file()
            print('\nFinish.\n')

        elif self.__options.action == 'print_supported_languages':
            self.__requester.print_supported_languages()

        elif self.__options.action == 'print_usage_info':
            self.__requester.print_usage_info()

    def __get_manager(self) -> managers.Manager:

        name, extension = os.path.splitext(self.__options.source_file)

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            return managers.DocumentManager(self.__requester, self.__options.source_file, self.__options.output_directory)
        if extension == '.json':
            return managers.JSONManager(self.__requester, self.__options.source_file, self.__options.output_directory)
        if extension == '.po':
            return managers.POManager(self.__requester, self.__options.source_file, self.__options.output_directory)
        return managers.TextManager(self.__requester, self.__options.source_file, self.__options.output_directory)
