#!/usr/bin/env python3

# ! Do not move colorama init. Autoreset works only here
from colorama import init

init(autoreset=True)

import os
import colorama
from polyglot import deepl, handlers, arguments, license

DOCUMENTS_SUPPORTED_BY_DEEPL: list[str] = [".docx", ".pptx", ".html", ".htm"]


class Polyglot:
    __options: arguments.Arguments
    __dispatcher: deepl.Deepl

    def __init__(self, arguments: arguments.Arguments):
        self.__options = arguments

    @property
    def __license_manager(self) -> license.LicenseManager:
        return self.__options.license_manager

    def execute_command(self):

        if self.__options.action == "set_license":
            self.__license_manager.set_license()
            return

        self.__dispatcher = deepl.Deepl(
            target_lang=self.__options.target_lang,
            source_lang=self.__options.source_lang,
            license_manager=self.__license_manager,
        )

        if self.__options.action == "translate":
            handler: handlers.Handler = self.__get_handler()
            handler.translate_source_file()
            print(f"\n{colorama.Fore.GREEN}Finish.\n")

        elif self.__options.action == "print_supported_languages":
            self.__dispatcher.print_supported_languages()

        elif self.__options.action == "print_usage_info":
            self.__dispatcher.print_usage_info()

    def __get_handler(self) -> handlers.Handler:

        extension: str = os.path.splitext(self.__options.source_file)[1]

        if extension in DOCUMENTS_SUPPORTED_BY_DEEPL:
            return handlers.DocumentHandler(
                self.__dispatcher,
                self.__options.source_file,
                self.__options.output_directory,
            )

        if extension == ".json":
            return handlers.JSONHandler(
                self.__dispatcher,
                self.__options.source_file,
                self.__options.output_directory,
            )

        if extension == ".po":
            return handlers.POHandler(
                self.__dispatcher,
                self.__options.source_file,
                self.__options.output_directory,
            )

        return handlers.TextHandler(
            self.__dispatcher,
            self.__options.source_file,
            self.__options.output_directory,
        )
