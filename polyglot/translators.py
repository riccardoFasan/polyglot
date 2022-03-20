import asyncio
from abc import ABC, abstractmethod
from typing import Any

import colorama
import progressbar

from polyglot import deepl


class Translator(ABC):

    _target_lang: str
    _source_lang: str
    _dispatcher: deepl.Deepl

    def __init__(
        self, target_lang: str, source_lang: str, dispatcher: deepl.Deepl
    ) -> None:
        self._target_lang = target_lang
        self._source_lang = source_lang
        self._dispatcher = dispatcher

    @abstractmethod
    def translate(self, content: Any) -> Any:
        pass


class TextTranslator(Translator):
    def translate(self, content: str) -> str:
        return self._dispatcher.translate(content, self._target_lang, self._source_lang)


class DictionaryTranslator(Translator):

    __progress_bar: progressbar.ProgressBar
    __completion_count: int = 0
    __not_translated_entries: list[str] = []

    def translate(self, content: dict) -> dict:
        self.__set_progress_bar(content)
        self.__translate_dictionary(content)
        self.__print_messages()
        return content

    def __set_progress_bar(self, content: dict) -> None:
        number_of_translations: int = self.__get_number_of_translations(content)
        self.__progress_bar = progressbar.ProgressBar(
            max_value=number_of_translations, redirect_stdout=True
        )

    def __get_number_of_translations(self, dictionary: dict) -> int:
        return sum(
            self.__get_number_of_translations(value) if isinstance(value, dict) else 1
            for key, value in dictionary.items()
        )

    def __translate_dictionary(self, dictionary: dict) -> None:

        for key, value in dictionary.items():

            if isinstance(value, dict):
                self.__translate_dictionary(value)

            else:
                dictionary[key] = self.__translate_entry(value)
                self.__completion_count += 1
                self.__progress_bar.update(self.__completion_count)

    def __translate_entry(self, entry: str) -> str:
        translation: str = self._dispatcher.translate(
            entry, self._target_lang, self._source_lang
        )
        if not translation:
            self.__not_translated_entries.append(entry)
        return translation if translation else entry

    def __print_messages(self) -> None:
        print("\nTranslation completed.")
        if len(self.__not_translated_entries) > 0:
            print(
                f"{colorama.Fore.YELLOW}\nThe following entries have not been translated:\n"
            )
            for entry in self.__not_translated_entries:
                print(f'{colorama.Fore.RESET}"{entry}"\n')


class DocumentTranslator(Translator):

    __document_id: str
    __document_key: str
    __translated_file: bytes

    def translate(self, content: str) -> bytes:
        document_data: dict[str, str] = self._dispatcher.translate_document(
            content, self._target_lang, self._source_lang
        )
        self.__document_id = document_data["document_id"]
        self.__document_key = document_data["document_key"]
        asyncio.run(self.__download_document_when_ready())
        return self.__translated_file

    async def __download_document_when_ready(self) -> None:
        status_data = self._dispatcher.check_document_status(
            self.__document_id, self.__document_key
        )
        status: str = status_data["status"]

        if status == "done":
            billed_characters: str = status_data["billed_characters"]
            print(f"Translation completed. Billed characters: {billed_characters}.")
            self.__translated_file = self.__download_target_file()
            return

        # * sometimes there are no seconds even if it's still translating
        if "seconds_remaining" in status_data:
            print(f'Remaining {status_data["seconds_remaining"]} seconds...')

        await self.__download_document_when_ready()

    def __download_target_file(self) -> bytes:
        return self._dispatcher.download_translated_document(
            self.__document_id, self.__document_key
        )
