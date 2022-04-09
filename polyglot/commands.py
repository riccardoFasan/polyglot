import asyncio
import json
from typing import Any
from requests.models import Response
from abc import ABC, abstractmethod

import colorama

import polyglot
from polyglot import license, clients
from polyglot.exceptions import DeeplException
from polyglot.utilities import get_color_by_percentage, get_truncated_text

class DeeplCommand(ABC):

    _license: license.License
    _client: clients.DeeplClient

    def __init__(self, license: license.License):
        self._license = license
        self._client = clients.DeeplClient(self._license)

    @abstractmethod
    def execute(self) -> Any:
        pass

class TranslateCommand(DeeplCommand, ABC):

    _content: Any
    _target_lang: str
    _source_lang: str

    def __init__(
        self, license: license.License, content: Any, target_lang: str, source_lang: str
    ):
        super().__init__(license)
        self._content = content
        self._target_lang = target_lang
        self._source_lang = source_lang

    @abstractmethod
    def execute(self) -> Any:
        pass


class PrintUsageInfo(DeeplCommand):
    def execute(self) -> None:
        response: Response = self._client.get_usage_info()

        try:
            body: dict[str, int] = json.loads(response.text)
            character_count: int = body["character_count"]
            character_limit: int = body["character_limit"]
            percentage: int = round((character_count / character_limit) * 100)
            print_color: str = get_color_by_percentage(percentage)
            print(
                f"\nPolyglot version: {polyglot.__version__}\nAPI key: {self._license.key}\nCharacters limit: {character_limit}\n{print_color}Used characters: {character_count} ({percentage}%)\n"
            )

        except:
            raise DeeplException(
                status_code=response.status_code, message="Error retrieving usage info"
            )


class PrintSupportedLanguages(DeeplCommand):
    def execute(self) -> None:
        response: Response = self._client.get_supported_languages()

        try:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        except:
            raise DeeplException(
                status_code=response.status_code,
                message="Error retrieving the supported languages.",
            )


class TranslateText(TranslateCommand):

    __LEN_LIMIT: int = 150

    def execute(self) -> str:
    
        truncated_text: str = get_truncated_text(self._content, self.__LEN_LIMIT)
        response:Response = self._client.translate(self._content, self._target_lang, self._source_lang)

        try:

            body: dict = json.loads(response.text)
            translation: str = body["translations"][0]["text"]

            truncated_translation: str = get_truncated_text(
                translation, self.__LEN_LIMIT
            )
            print(f'"{truncated_text}" => "{truncated_translation}"')
            return translation

        except KeyError:
            message: str = json.loads(response.text)["message"]
            if message:
                raise DeeplException(
                    status_code=response.status_code,
                    message=f'Error translating "{truncated_text}". Message: {message}"\n',
                )
            print(
                f'{colorama.Fore.YELLOW}\nNo traslation found for "{truncated_text}"!\n'
            )

        except:
            raise DeeplException(
                status_code=response.status_code,
                message=f'Error translating "{truncated_text}".\n',
            )
        return ""


class TranslateDocumentCommand(TranslateCommand):

    __document: bytes

    def execute(self) -> bytes:
        document_data: dict[str, str] = self.__send_document()
        asyncio.run(self.__get_document(document_data))
        return self.__document

    def __send_document(self) -> dict[str, str]:

        response: Response = self._client.upload_document(self._content, self._target_lang, self._source_lang)

        if response.status_code == 200:
            return json.loads(response.text)

        raise DeeplException(
            status_code=response.status_code,
            message=f'Error translating document "{self._content}"',
        )

    async def __get_document(self, document_data: dict[str, str]) -> None:
        status_data = self.__check_document_status(
            document_data["document_id"], document_data["document_key"]
        )
        status: str = status_data["status"]

        if status == "done":
            billed_characters: str = status_data["billed_characters"]
            print(f"Translation completed. Billed characters: {billed_characters}.")
            self.__document = self.__download_translated_document(
                document_data["document_id"], document_data["document_key"]
            )
            return

        # * sometimes there are no seconds even if it's still translating
        if "seconds_remaining" in status_data:
            print(f'Remaining {status_data["seconds_remaining"]} seconds...')

        await self.__get_document(document_data)

    def __check_document_status(
        self, document_id: str, document_key: str
    ) -> dict[str, str]:
        response: Response = self._client.get_document_status(document_id, document_key)

        if response.status_code == 200:
            return json.loads(response.text)

        raise DeeplException(
            status_code=response.status_code,
            message="Error checking the status of a document",
        )

    def __download_translated_document(
        self, document_id: str, document_key: str
    ) -> bytes:
        response: Response = self._client.download_document(document_id, document_key)

        if response.status_code == 200:
            return response.content

        raise DeeplException(
            status_code=response.status_code, message="Error downlaoding a document."
        )
        