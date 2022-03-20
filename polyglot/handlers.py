import json
import os
import polib
from abc import ABC, abstractmethod
from typing import Any

from polyglot.errors import HandlerError

# TODO: Check if the file is empty
def verfiy_source(function: Any) -> Any:
    def function_wrapper(instance: FileHandler):
        try:
            return function(instance)
        except FileNotFoundError:
            raise HandlerError(instance.source_file, "File not found.")
        except:
            raise HandlerError(instance.source_file, "File not supported.")

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

    @property
    def _extension(self) -> str:
        return os.path.splitext(self.source_file)[1]

    def __set_target_file(self, output_directory: str, target_lang: str) -> None:
        output_directory = (
            output_directory
            if output_directory and os.path.isdir(output_directory)
            else os.getcwd()
        )
        if output_directory[-1] == "/":
            output_directory = output_directory[:-1]
        self._target_file = f"{output_directory}/{target_lang.lower()}{self._extension}"

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def write(self, translated_content: Any) -> None:
        pass


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

        pofile: polib.POFile = self.__pofile_source
        translatables: dict[str, str] = {}

        for entry in pofile:
            message: str = entry.msgid if entry.msgstr == "" else entry.msgstr
            self.__content[entry.msgid] = {
                "msgstr": message,
                "occurrences": entry.occurrences,
            }
            translatables[entry.msgid] = message

        return translatables

    @property
    def __pofile_source(self) -> polib.POFile:
        return polib.pofile(self.source_file)

    def write(self, translated_content: dict[str, str]) -> None:
        pofile: polib.POFile = polib.POFile()
        pofile.metadata = self.__pofile_source.metadata

        self.__update_content(translated_content)

        for key, value in self.__content.items():
            entry: polib.POEntry = polib.POEntry(
                msgid=key, msgstr=value["msgstr"], occurrences=value["occurrences"]
            )
            pofile.append(entry)

        pofile.save(self._target_file)
        mofile_path: str = f"{ os.path.splitext(self._target_file)[0]}.mo"
        pofile.save_as_mofile(mofile_path)

        print(f"Generated {self._target_file} and {mofile_path}.")

    def __update_content(self, translated_content: dict[str, str]) -> None:
        for key, value in translated_content.items():
            self.__content[key]["msgstr"] = value


class DocumentHandler(FileHandler):
    @verfiy_source
    def read(self) -> str:
        with open(self.source_file, "r") as source:
            return self.source_file

    def write(self, translated_content: bytes) -> None:
        with open(self._target_file, "wb+") as destination:
            destination.write(translated_content)
            print(f"Generated {self._target_file}.")
