from abc import ABC, abstractmethod
import asyncio
import json
from typing import Any
import requests
import urllib.parse
from requests.models import Response

import colorama

import polyglot
from polyglot import license
from polyglot.exceptions import DeeplException
from polyglot.utilities import get_color_by_percentage, get_truncated_text
from polyglot.connectors import connector


class DeeplConnectorData:

    _license: license.License

    def __init__(self, license: license.License) -> None:
        self._license = license

    @property
    def base_url(self) -> str:
        version: str = (
            "" if self._license.version == license.LicenseVersion.PRO else "-free"
        )
        return f"https://api{version}.deepl.com/v2/"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"DeepL-Auth-Key {self._license.key}",
            "Content-Type": "application/json",
        }


class DeeplCommand(ABC):

    _license: license.License
    _request_data: DeeplConnectorData

    def __init__(self, license: license.License):
        self._license = license
        self._request_data = DeeplConnectorData(self._license)

    @abstractmethod
    def execute(self) -> Any:
        pass


class PrintUsageInfo(DeeplCommand):
    def execute(self) -> None:
        response: Response = self.__get_usage_info()

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

    def __get_usage_info(self) -> Response:
        return requests.get(
            f"{self._request_data.base_url}usage", headers=self._request_data.headers
        )


class PrintSupportedLanguages(DeeplCommand):
    def execute(self) -> None:
        response: Response = requests.get(
            f"{self._request_data.base_url}languages",
            headers=self._request_data.headers,
        )

        try:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        except:
            raise DeeplException(
                status_code=response.status_code,
                message="Error retrieving the supported languages.",
            )


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


class TranslateText(TranslateCommand):

    __LEN_LIMIT: int = 150

    def execute(self) -> str:
        escaped_content: str = urllib.parse.quote(self._content)
        endpoint: str = f"{self._request_data.base_url}translate?auth_key={self._license.key}&text={escaped_content}&target_lang={self._target_lang}"

        if self._source_lang != "":
            endpoint += f"&source_lang={self._source_lang}"

        response: Response = requests.get(endpoint)
        truncated_text: str = get_truncated_text(self._content, self.__LEN_LIMIT)

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
        request_data: dict[str, str] = {
            "target_lang": self._target_lang,
            "auth_key": self._license.key,
            "filename": self._content,
        }

        if self._source_lang != "":
            request_data["source_lang"] = self._source_lang

        endpoint: str = f"{self._request_data.base_url}document/"

        with open(self._content, "rb") as document:
            response: Response = requests.post(
                endpoint, data=request_data, files={"file": document}
            )

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
        endpoint: str = f"{self._request_data.base_url}document/{document_id}?auth_key={self._license.key}&document_key={document_key}"
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return json.loads(response.text)

        raise DeeplException(
            status_code=response.status_code,
            message="Error checking the status of a document",
        )

    def __download_translated_document(
        self, document_id: str, document_key: str
    ) -> bytes:
        endpoint: str = f"{self._request_data.base_url}document/{document_id}/result?auth_key={self._license.key}&document_key={document_key}"
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return response.content

        raise DeeplException(
            status_code=response.status_code, message="Error downlaoding a document."
        )


class DeeplConnector(connector.EngineConnector):
    def print_usage_info(self) -> None:
        command: PrintUsageInfo = PrintUsageInfo(self._license)
        return command.execute()

    def print_supported_languages(self) -> None:
        command: PrintSupportedLanguages = PrintSupportedLanguages(self._license)
        return command.execute()

    def translate(self, content: str, target_lang: str, source_lang: str = "") -> str:
        command: TranslateText = TranslateText(
            self._license, content, target_lang, source_lang
        )
        return command.execute()

    def translate_document(
        self, source_file: str, target_lang: str, source_lang: str = ""
    ) -> bytes:
        command: TranslateDocumentCommand = TranslateDocumentCommand(
            self._license, source_file, target_lang, source_lang
        )
        return command.execute()
