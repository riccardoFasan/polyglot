import os
from dataclasses import dataclass
from typing import Any
import colorama
from colorama import init
from polyglot import deepl, handlers, arguments, license, translators

# ! Do not move colorama init. Autoreset works only here
init(autoreset=True)


DOCUMENTS_SUPPORTED_BY_DEEPL: list[str] = [".docx", ".pptx", ".html", ".htm"]


@dataclass
class FileTranslator:
    handler: handlers.FileHandler
    translator: translators.Translator


class Polyglot:
    __arguments: arguments.Arguments
    __dispatcher: deepl.Deepl

    def __init__(self, arguments: arguments.Arguments):
        self.__arguments = arguments

    @property
    def __license_manager(self) -> license.LicenseManager:
        return self.__arguments.license_manager

    def execute_command(self):

        if self.__arguments.action == "set_license":
            self.__license_manager.set_license()
            return

        self.__dispatcher = deepl.Deepl(
            license_manager=self.__license_manager,
        )

        if self.__arguments.action == "translate":
            file_translator: FileTranslator = self.__get_file_translator()
            content: Any = file_translator.handler.read()
            translated_content: Any = file_translator.translator.translate(content)
            file_translator.handler.write(translated_content)
            print(f"\n{colorama.Fore.GREEN}Finish.\n")

        elif self.__arguments.action == "print_supported_languages":
            self.__dispatcher.print_supported_languages()

        elif self.__arguments.action == "print_usage_info":
            self.__dispatcher.print_usage_info()

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

        if extension == ".po":
            return handlers.POHandler(**file_handler_options)

        return handlers.TextHandler(**file_handler_options)

    def __get_translator(self, extension: str) -> translators.Translator:

        translator_options: dict[str, Any] = {
            "target_lang": self.__arguments.target_lang,
            "source_lang": self.__arguments.source_lang,
            "dispatcher": self.__dispatcher,
        }

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            return translators.DocumentTranslator(**translator_options)

        if extension == ".json" or extension == ".po":
            return translators.DictionaryTranslator(**translator_options)

        return translators.TextTranslator(**translator_options)
