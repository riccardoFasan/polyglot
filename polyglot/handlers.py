import os
import json
from abc import ABC, abstractmethod

import polib
import colorama
import progressbar

from polyglot import deepl


class Handler(ABC):

    def __init__(self, requester: deepl.Deepl, source_file: str, output_directory: str = '') -> None:
        self.source_file = source_file
        self.__check_source_file()
        self.requester = requester
        self.output_directory = output_directory if output_directory != '' and os.path.isdir(
            output_directory) else os.getcwd()

    @property
    def _extension(self) -> str:
        name, extension = os.path.splitext(self.source_file)
        return extension

    @property
    def _target_file(self) -> str:
        return f'{self.output_directory}/{self.requester.target_lang.lower()}{self._extension}'

    def __check_source_file(self) -> None:
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(
                f'{colorama.Fore.RED}\n"{self.source_file}" wan not found!')

    @abstractmethod
    def translate_source_file(self) -> None:
        pass


class TextHandler(Handler):

    content: str = ''

    def translate_source_file(self) -> None:
        self._load_source_content()
        self._translate_content()
        if self.content:
            self._make_translated_files()

    def _load_source_content(self) -> None:
        try:
            with open(self.source_file, 'r') as source:
                self.content = source.read()
        except:
            quit(f'{colorama.Fore.RED}Cannot read {self._extension} files.')

    def _translate_content(self) -> None:
        self.content = self.requester.translate(self.content)

    def _make_translated_files(self) -> None:
        with open(self._target_file, 'w+') as destination:
            destination.write(self.content)
            print(f'Generated {self._target_file}.')


# ! Liskov substitution principle violation: extended classes JSONHandler and POHandler are manipulating self.content in ways completelly differents
class DictionaryHandler(TextHandler):

    completion_count: int = 0
    not_translated_entries: list[str] = []
    progress_bar: progressbar.ProgressBar
    content: dict = dict()

    def translate_source_file(self) -> None:
        self._load_source_content()
        self.progress_bar = self.__get_progress_bar()
        self._translate_content()
        self.__print_ending_messages()
        self._make_translated_files()

    def __get_progress_bar(self) -> progressbar.ProgressBar:
        number_of_translations: int = self._get_number_of_translations()
        return progressbar.ProgressBar(max_value=number_of_translations, redirect_stdout=True)

    def _get_number_of_translations(self) -> int:
        return 0

    def __print_ending_messages(self) -> None:
        print('\nTranslation completed.')
        if len(self.not_translated_entries) > 0:
            print(
                f'{colorama.Fore.YELLOW}\n{len(self.not_translated_entries)} entries have not been translated:\n')
            for entry in self.not_translated_entries:
                print(f'"{entry}"')
            print(colorama.Fore.RESET)

    def _translate_and_handle(self, entry: str) -> str:
        translation: str | None = self.requester.translate(entry)
        if not translation:
            self.not_translated_entries.append(entry)
        return translation if translation else entry


class JSONHandler(DictionaryHandler):

    def _get_number_of_translations(self, dictionary: dict[str, str] | None = None) -> int:
        if not dictionary:
            dictionary = self.content
        return sum(self._get_number_of_translations(value) if isinstance(value, dict) else 1 for key, value in dictionary.items())

    def _load_source_content(self) -> None:
        with open(self.source_file, 'r') as source:
            self.content = json.load(source)

    def _translate_content(self, dictionary: dict[str, str] | None = None) -> None:

        if not dictionary:
            dictionary = self.content

        for key, value in dictionary.items():

            if isinstance(value, dict):
                self._translate_content(value)

            else:
                dictionary[key] = self._translate_and_handle(value)
                self.completion_count += 1
                self.progress_bar.update(self.completion_count)

    def _make_translated_files(self) -> None:
        with open(self._target_file, 'w+') as destination:
            destination.write(json.dumps(self.content, indent=2))
            print(f'Generated {self._target_file}.')


class POHandler(DictionaryHandler):

    @property
    def __pofile_source(self) -> polib.POFile:
        return polib.pofile(self.source_file)

    def _get_number_of_translations(self) -> int:
        return len(self.content.items())

    def _load_source_content(self) -> None:
        pofile: polib.POFile = self.__pofile_source

        for entry in pofile:
            self.content[entry.msgid] = {
                "msgstr": entry.msgid if entry.msgstr == '' else entry.msgstr,
                "occurrences": entry.occurrences
            }

    def _translate_content(self) -> None:
        for key, value in self.content.items():
            value['msgstr'] = self._translate_and_handle(value['msgstr'])
            self.completion_count += 1
            self.progress_bar.update(self.completion_count)

    def _make_translated_files(self) -> None:
        pofile: polib.POFile = polib.POFile()
        pofile.metadata = self.__pofile_source.metadata

        for key, value in self.content.items():
            entry: polib.POEntry = polib.POEntry(
                msgid=key,
                msgstr=value["msgstr"],
                occurrences=value['occurrences']
            )
            pofile.append(entry)

        pofile.save(self._target_file)

        mofile: str = f'{self.output_directory}/{self.requester.target_lang.lower()}.mo'
        pofile.save_as_mofile(mofile)
        print(f'Generated {self._target_file} and {mofile}.')


class DocumentHandler(Handler):

    __document_id: str = ''
    __document_key: str = ''

    def translate_source_file(self) -> None:
        document_data: dict[str, str] = self.requester.translate_document(
            self.source_file)
        self.__document_id = document_data['document_id']
        self.__document_key = document_data['document_key']
        self.__download_document_when_ready()

    def __download_document_when_ready(self) -> None:
        status_data = self.requester.check_document_status(
            self.__document_id, self.__document_key)
        status: str = status_data['status']

        if status == 'done':
            billed_characters: str = status_data['billed_characters']
            print(
                f'Translation completed. Billed characters: {billed_characters}.')
            self.__download_target_file()
            return

        # * sometimes there are no seconds even if it's still translating
        if 'seconds_remaining' in status_data:
            print(f'Remaining {status_data["seconds_remaining"]} seconds...')

        self.__download_document_when_ready()

    def __download_target_file(self) -> None:
        binaries: bytes = self.requester.download_translated_document(
            self.__document_id, self.__document_key)
        with open(self._target_file, 'wb+') as destination:
            destination.write(binaries)
            print(f'Generated {self._target_file}.')
