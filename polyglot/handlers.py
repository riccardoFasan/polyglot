import json
import os
from abc import ABC, abstractmethod
from typing import Any, Callable

import polib

from polyglot.utils import DownloadedDocumentStream
from polyglot.errors import HandlerError


def verfiy_source(function: Callable) -> Callable:
    def function_wrapper(instance: FileHandler):
        try:
            return function(instance)
        except FileNotFoundError:
            HandlerError("File not found", instance.source_file)
        except:
            HandlerError("File not supported", instance.source_file)
    return function_wrapper


class FileHandler(ABC):

    source_file: str
    _target_file: str

    def __init__(
        self, source_file: str, output_directory: str, target_lang: str
    ) -> None:
        self.source_file = source_file
        self.target_lang = target_lang
        self.__set_target_file(output_directory, target_lang)

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def write(self, translated_content: Any) -> None:
        pass

    @property
    def _extension(self) -> str:
        return os.path.splitext(self.source_file)[1]

    def __set_target_file(self, output_directory: str, target_lang: str) -> None:
        output_directory = (
            output_directory
            if output_directory != "" and os.path.isdir(output_directory)
            else os.getcwd()
        )
        if output_directory[-1] == "/":
            output_directory = output_directory[:-1]
        self._target_file = f"{output_directory}/{target_lang.lower()}{self._extension}"


class TextHandler(FileHandler):
    @verfiy_source
    def read(self) -> str:
        with open(self.source_file, "r") as source:
            return source.read()

    def write(self, translated_content: str) -> None:
        with open(self._target_file, "w+") as destination:
            destination.write(translated_content)
            print(f"Generated {self._target_file}.")


class JSONHandler(FileHandler):
    @verfiy_source
    def read(self) -> dict:
        with open(self.source_file, "r") as source:
            return json.load(source)

    def write(self, translated_content: dict) -> None:
        with open(self._target_file, "w+") as destination:
            destination.write(json.dumps(translated_content, indent=2))
            print(f"Generated {self._target_file}.")


class POHandler(FileHandler):

    __content: dict[str, Any] = {}

    @verfiy_source
    def read(self) -> dict:

        translatables: dict[str, str] = {}

        for entry in self.__pofile_source:
            message: str = entry.msgid if entry.msgstr == "" else entry.msgstr
            self.__content[entry.msgid] = {
                "msgstr": message,
                "occurrences": entry.occurrences,
            }
            translatables[entry.msgid] = message

        return translatables

    def write(self, translated_content: dict[str, str]) -> None:
        pofile: polib.POFile = polib.POFile()
        pofile.metadata = self.__pofile_source.metadata

        self.__update_content(translated_content)

        for key, value in self.__content.items():
            entry: polib.POEntry = polib.POEntry(
                msgid=key, msgstr=value["msgstr"], occurrences=value["occurrences"]
            )
            pofile.append(entry)

        basename: str = os.path.splitext(self._target_file)[0]
        pofile.save(f"{basename}.po")
        pofile.save_as_mofile(f"{basename}.mo")

        print(f"Generated {basename}.po and {basename}.mo.")

    @property
    def __pofile_source(self) -> polib.POFile:
        return polib.pofile(self.source_file)

    def __update_content(self, translated_content: dict[str, str]) -> None:
        for key, value in translated_content.items():
            self.__content[key]["msgstr"] = value


class DocumentHandler(FileHandler):
    @verfiy_source
    def read(self) -> str:
        return self.source_file

    def write(self, translated_content: DownloadedDocumentStream) -> None:
        if translated_content:
            with open(self._target_file, "wb+") as destination:
                for chunk in translated_content:
                    destination.write(chunk)
                print(f"Generated {self._target_file}.")
