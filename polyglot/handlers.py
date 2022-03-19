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
        self._target_file = f"{output_directory}/{target_lang.lower()}{self._extension}"

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def write(self, content: Any) -> None:
        pass


class TextHandler(FileHandler):
    @verfiy_source
    def read(self) -> str:
        with open(self.source_file, "r") as source:
            return source.read()

    def write(self, content: str) -> None:
        with open(self._target_file, "w+") as destination:
            destination.write(content)
            print(f"Generated {self._target_file}.")


class JSONHandler(FileHandler):
    @verfiy_source
    def read(self) -> dict:
        with open(self.source_file, "r") as source:
            return json.load(source)

    def write(self, content: dict) -> None:
        with open(self._target_file, "w+") as destination:
            destination.write(json.dumps(content, indent=2))
            print(f"Generated {self._target_file}.")


class POHandler(FileHandler):
    @verfiy_source
    def read(self) -> dict:
        pofile: polib.POFile = self.__pofile_source
        content: dict = {}

        for entry in pofile:
            content[entry.msgid] = {
                "msgstr": entry.msgid if entry.msgstr == "" else entry.msgstr,
                "occurrences": entry.occurrences,
            }

        return content

    @property
    def __pofile_source(self) -> polib.POFile:
        return polib.pofile(self.source_file)

    def write(self, content: dict) -> None:
        pofile: polib.POFile = polib.POFile()
        pofile.metadata = self.__pofile_source.metadata

        for key, value in content.items():
            entry: polib.POEntry = polib.POEntry(
                msgid=key, msgstr=value["msgstr"], occurrences=value["occurrences"]
            )
            pofile.append(entry)

        pofile.save(self._target_file)
        mofile_path: str = f"{ os.path.splitext(self._target_file)[0]}.mo"
        pofile.save_as_mofile(mofile_path)

        print(f"Generated {self._target_file} and {mofile_path}.")


class DocumentHandler(FileHandler):
    @verfiy_source
    def read(self) -> str:
        with open(self.source_file, "r") as source:
            return self.source_file

    def write(self, content: bytes) -> None:
        with open(self._target_file, "wb+") as destination:
            destination.write(content)
            print(f"Generated {self._target_file}.")
