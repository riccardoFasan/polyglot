import asyncio
import json
import requests
import urllib.parse
from requests.models import Response
from abc import ABC, abstractmethod

import colorama

import polyglot
from polyglot import license
from polyglot.errors import DeeplError
from polyglot.utilities import get_color_by_percentage, get_truncated_text


class TranslationEngine(ABC):
    @abstractmethod
    def print_usage_info(self) -> None:
        pass

    @abstractmethod
    def print_supported_languages(self) -> None:
        pass

    @abstractmethod
    def translate(self, entry: str, target_lang: str, source_lang: str = "") -> str:
        pass

    @abstractmethod
    def translate_document(
        self, source_file: str, target_lang: str, source_lang: str = ""
    ) -> bytes:
        pass


class DeeplEngine(TranslationEngine):

    __LEN_LIMIT: int = 150

    __license: license.License
    __license_manager: license.LicenseManager

    __document: bytes

    def __init__(
        self,
        license_manager: license.LicenseManager,
    ) -> None:
        self.__license_manager = license_manager
        self.__license = self.__license_manager.get_license()

    @property
    def __base_url(self) -> str:
        version: str = (
            "" if self.__license.version == license.LicenseVersion.PRO else "-free"
        )
        return f"https://api{version}.deepl.com/v2/"

    @property
    def __headers(self) -> dict[str, str]:
        return {
            "Authorization": f"DeepL-Auth-Key {self.__license.key}",
            "Content-Type": "application/json",
        }

    def __get_usage_info(self) -> Response:
        return requests.get(f"{self.__base_url}usage", headers=self.__headers)

    def print_usage_info(self) -> None:
        response: Response = self.__get_usage_info()

        try:
            body: dict[str, int] = json.loads(response.text)
            character_count: int = body["character_count"]
            character_limit: int = body["character_limit"]
            percentage: int = round((character_count / character_limit) * 100)
            print_color: str = get_color_by_percentage(percentage)
            print(
                f"\nPolyglot version: {polyglot.__version__}\nAPI key: {self.__license.key}\nCharacters limit: {character_limit}\n{print_color}Used characters: {character_count} ({percentage}%)\n"
            )

        except:
            raise DeeplError(
                status_code=response.status_code, message="Error retrieving usage info"
            )

    def print_supported_languages(self) -> None:
        response: Response = requests.get(
            f"{self.__base_url}languages", headers=self.__headers
        )

        try:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        except:
            raise DeeplError(
                status_code=response.status_code,
                message="Error retrieving the supported languages.",
            )

    def translate(self, entry: str, target_lang: str, source_lang: str = "") -> str:

        escaped_entry: str = urllib.parse.quote(entry)
        endpoint: str = f"{self.__base_url}translate?auth_key={self.__license.key}&text={escaped_entry}&target_lang={target_lang}"

        if source_lang != "":
            endpoint += f"&source_lang={source_lang}"

        response: Response = requests.get(endpoint)
        truncated_text: str = get_truncated_text(entry, self.__LEN_LIMIT)

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
                raise DeeplError(
                    status_code=response.status_code,
                    message=f'Error translating "{truncated_text}". Message: {message}"\n',
                )
            print(
                f'{colorama.Fore.YELLOW}\nNo traslation found for "{truncated_text}"!\n'
            )

        except:
            raise DeeplError(
                status_code=response.status_code,
                message=f'Error translating "{truncated_text}".\n',
            )
        return ""

    def translate_document(
        self, source_file: str, target_lang: str, source_lang: str = ""
    ) -> bytes:
        document_data: dict[str, str] = self.__send_document(
            source_file, target_lang, source_lang
        )
        asyncio.run(self.__get_document(document_data))
        return self.__document

    def __send_document(
        self, source_file: str, target_lang: str, source_lang: str = ""
    ) -> dict[str, str]:
        request_data: dict[str, str] = {
            "target_lang": target_lang,
            "auth_key": self.__license.key,
            "filename": source_file,
        }

        if source_lang != "":
            request_data["source_lang"] = source_lang

        endpoint: str = f"{self.__base_url}document/"

        with open(source_file, "rb") as document:
            response: Response = requests.post(
                endpoint, data=request_data, files={"file": document}
            )

            if response.status_code == 200:
                return json.loads(response.text)

        raise DeeplError(
            status_code=response.status_code,
            message=f'Error translating document "{source_file}"',
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
        endpoint: str = f"{self.__base_url}document/{document_id}?auth_key={self.__license.key}&document_key={document_key}"
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return json.loads(response.text)

        raise DeeplError(
            status_code=response.status_code,
            message="Error checking the status of a document",
        )

    def __download_translated_document(
        self, document_id: str, document_key: str
    ) -> bytes:
        endpoint: str = f"{self.__base_url}document/{document_id}/result?auth_key={self.__license.key}&document_key={document_key}"
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return response.content

        raise DeeplError(
            status_code=response.status_code, message="Error downlaoding a document."
        )
