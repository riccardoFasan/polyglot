import os
from dataclasses import dataclass
from typing import Any

import colorama
from colorama import init

from polyglot import handlers, arguments, license, translators, connectors

# ! Do not move colorama init. Autoreset works only here
init(autoreset=True)

DOCUMENTS_SUPPORTED_BY_DEEPL: list[str] = [".docx", ".pptx", ".html", ".htm", ".pdf"]


@dataclass
class FileTranslator:
    handler: handlers.FileHandler
    translator: translators.Translator


class Polyglot:
    __arguments: arguments.Arguments
    __connector: connectors.EngineConnector

    def __init__(self, arguments: arguments.Arguments):
        self.__arguments = arguments

    def execute_command(self):

        if self.__arguments.action == "set-license":
            self.__license_manager.set_license()
            return

        self.__connector = connectors.DeeplConnector(
            license_manager=self.__license_manager,
        )

        if self.__arguments.action == "translate":
            file_translator: FileTranslator = self.__get_file_translator()
            content: Any = file_translator.handler.read()
            translated_content: Any = file_translator.translator.translate(content)
            file_translator.handler.write(translated_content)
            print(f"\n{colorama.Fore.GREEN}Finish.\n{colorama.Fore.RESET}")

        elif self.__arguments.action == "languages":
            self.__connector.print_supported_languages()

        elif self.__arguments.action == "info":
            self.__connector.print_usage_info()

    @property
    def __license_manager(self) -> license.LicenseManager:
        return self.__arguments.license_manager

    def __get_file_translator(self) -> FileTranslator:
        extension: str = os.path.splitext(self.__arguments.source_file)[1]
        handler: handlers.FileHandler = self.__get_handler(extension)
        translator: translators.Translator = self.__get_translator(extension)
        return FileTranslator(handler=handler, translator=translator)

    def __get_handler(self, extension: str) -> handlers.FileHandler:

        file_handler_options: dict[str, str] = {
            "source_file": self.__arguments.source_file,
            "output_directory": self.__arguments.output_directory,
            "target_lang": self.__arguments.target_lang,
        }

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            return handlers.DocumentHandler(**file_handler_options)

        if extension == ".json":
            return handlers.JSONHandler(**file_handler_options)

        if extension == ".po" or extension == ".pot":
            return handlers.POHandler(**file_handler_options)

        return handlers.TextHandler(**file_handler_options)

    def __get_translator(self, extension: str) -> translators.Translator:

        translator_options: dict[str, Any] = {
            "target_lang": self.__arguments.target_lang,
            "source_lang": self.__arguments.source_lang,
            "connector": self.__connector,
        }

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            return translators.DocumentTranslator(**translator_options)

        if extension == ".json" or extension == ".po" or extension == ".pot":
            return translators.DictionaryTranslator(**translator_options)

        return translators.TextTranslator(**translator_options)
