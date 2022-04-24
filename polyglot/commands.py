import asyncio
from typing import Any, Callable, Optional
from abc import ABC, abstractmethod

import colorama
import deepl

import polyglot
from polyglot.utils import (
    DownloadedDocumentStream,
    get_color_by_percentage,
    get_truncated_text,
)
from polyglot.errors import DeeplError


def handle_error(function: Callable) -> Callable:
    def function_wrapper(instance: DeeplCommand):
        try:
            return function(instance)
        except deepl.DeepLException as error:
            DeeplError(error)

    return function_wrapper


class DeeplCommand(ABC):

    _license: str
    _translator: deepl.Translator

    def __init__(self, license: str) -> None:
        self._license = license
        self._translator = deepl.Translator(self._license)

    @abstractmethod
    def execute(self) -> Any:
        pass


class TranslateCommand(DeeplCommand, ABC):

    _content: Any
    _target_lang: str
    _source_lang: str

    def __init__(self, license: str, content: Any, target_lang: str, source_lang: str) -> None:
        super().__init__(license)
        self._content = content
        if target_lang == 'EN': # * EN as a target language is deprecated
            target_lang = 'EN-US'
        self._target_lang = target_lang
        self._source_lang = source_lang

    @abstractmethod
    def execute(self) -> Any:
        pass


class PrintUsageInfo(DeeplCommand):
    @handle_error
    def execute(self) -> None:
        usage: deepl.Usage = self._translator.get_usage()

        limit: Optional[int] = usage.character.limit
        count: Optional[int] = usage.character.count

        print(
            f"\nPolyglot version: {polyglot.__version__}\nDeepL version: {deepl.__version__}\nAPI key: {self._license}"
        )

        if limit is not None:
            print(f"Characters limit: {limit}")

        if count is not None:
            count_text: str = f"Used Characters: {count}"
            if limit is not None:
                percentage: int = round((count / limit) * 100)
                print_color: str = get_color_by_percentage(percentage)
                count_text += f" {print_color}({percentage}%)"
            print(count_text)


class PrintSupportedLanguages(DeeplCommand):
    @handle_error
    def execute(self) -> None:
        print("\nAvailable source languages:")
        for language in self._translator.get_source_languages():
            print(f"{language.name} ({language.code})")

        print("\nAvailable target languages:")
        for language in self._translator.get_target_languages():
            lang: str = f"{language.name} ({language.code})"
            if language.supports_formality:
                lang += " - formality supported"
            print(lang)


class TranslateText(TranslateCommand):

    __LEN_LIMIT: int = 150

    @handle_error
    def execute(self) -> str:
        truncated_text: str = get_truncated_text(self._content, self.__LEN_LIMIT)
        response: Any = self._translator.translate_text(
            [self._content],
            target_lang=self._target_lang,
            source_lang=self._source_lang,
        )
        try:
            translation: str = response[0].text
            truncated_translation: str = get_truncated_text(
                translation, self.__LEN_LIMIT
            )
            print(f'"{truncated_text}" => "{truncated_translation}"')
            return translation
        except KeyError:
            print(
                f'{colorama.Fore.YELLOW}\nNo traslation found for "{truncated_text}"!\n'
            )
        return ""


class TranslateDocumentCommand(TranslateCommand):

    __document: DownloadedDocumentStream
    __remaining: int = 0

    @handle_error
    def execute(self) -> DownloadedDocumentStream:
        document_data: deepl.DocumentHandle = self.__send_document()
        asyncio.run(self.__get_document(document_data))
        return self.__document

    def __send_document(self) -> deepl.DocumentHandle:
        with open(self._content, "rb") as document:
            return self._translator.translate_document_upload(
                document,
                target_lang=self._target_lang,
                source_lang=self._source_lang,
                filename=self._content,
            )

    async def __get_document(self, document_handle: deepl.DocumentHandle) -> None:
        status: deepl.DocumentStatus = self.__check_document_status(document_handle)

        if status.ok and status.done:
            print(
                f"Translation completed. Billed characters: {status.billed_characters}."
            )
            self.__document = self.__download_translated_document(document_handle)
            self.__remaining = 0
            return

        # * sometimes there are no seconds even if it's still translating
        if (
            status.seconds_remaining is not None
            and self.__remaining != status.seconds_remaining
        ):
            self.__remaining = status.seconds_remaining
            print(f"Remaining {status.seconds_remaining} seconds...")

        await self.__get_document(document_handle)

    def __check_document_status(
        self, document_handle: deepl.DocumentHandle
    ) -> deepl.DocumentStatus:
        return self._translator.translate_document_get_status(document_handle)

    def __download_translated_document(
        self, document_handle: deepl.DocumentHandle
    ) -> DownloadedDocumentStream:
        response: Any = self._translator.translate_document_download(document_handle)
        return response.iter_content()
