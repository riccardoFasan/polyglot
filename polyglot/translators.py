import asyncio
from concurrent.futures import ThreadPoolExecutor

from abc import ABC, abstractmethod
from typing import Any

import colorama
import progressbar

from polyglot import connectors
from polyglot.utils import DownloadedDocumentStream


class Translator(ABC):

    _target_lang: str
    _source_lang: str
    _connector: connectors.EngineConnector

    def __init__(
        self,
        target_lang: str,
        source_lang: str,
        connector: connectors.EngineConnector,
    ) -> None:
        self._target_lang = target_lang
        self._source_lang = source_lang
        self._connector = connector

    @abstractmethod
    def translate(self, content: Any) -> Any:
        pass


class TextTranslator(Translator):
    def translate(self, content: str) -> str:
        return self._connector.translate(content, self._target_lang, self._source_lang)


class DictionaryTranslator(Translator):

    __progress_bar: progressbar.ProgressBar
    __completion_count: int = 0
    __not_translated_entries: list[str] = []

    __loop:asyncio.AbstractEventLoop = asyncio.get_event_loop()
    __futures:list[asyncio.Future] = []
    __executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=30) # ? I honestly don't know whether it is too much or too little

    def translate(self, content: dict) -> dict:
        self.__set_progress_bar(content)
        self.__populate_futures(content)
        loop:asyncio.AbstractEventLoop = asyncio.get_event_loop()
        loop.run_until_complete(self.__translate_dictionary())
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

    def __populate_futures(self, dictionary: dict) -> None:
        for key, value in dictionary.items():

            if isinstance(value, dict):
                self.__populate_futures(value)

            else:
                self.__futures.append(self.__loop.run_in_executor(self.__executor, self.__translate_entry, value, dictionary,key))
             

    def __translate_entry(self, entry: str, dictionary:dict, key:str) -> None:
        translation: str = self._connector.translate(
            entry, self._target_lang, self._source_lang
        )
        if not translation:
            self.__not_translated_entries.append(entry)
        self.__completion_count += 1
        self.__progress_bar.update(self.__completion_count)
        dictionary[key] = translation if translation else entry

    async def __translate_dictionary(self) -> None :
        await asyncio.gather(*self.__futures)


    def __print_messages(self) -> None:
        print("\nTranslation completed.")
        if len(self.__not_translated_entries) > 0:
            print(
                f"{colorama.Fore.YELLOW}\nThe following entries have not been translated:\n"
            )
            for entry in self.__not_translated_entries:
                print(f'{colorama.Fore.RESET}"{entry}"\n')


class DocumentTranslator(Translator):
    def translate(self, content: str) -> DownloadedDocumentStream:
        return self._connector.translate_document(
            content, self._target_lang, self._source_lang
        )
