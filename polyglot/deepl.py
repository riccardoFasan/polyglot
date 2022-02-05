
import os
import requests
import json
import pathlib
import colorama
from dataclasses import dataclass
from requests.models import Response
from distutils.util import strtobool


@dataclass
class License:
    key: str = ''
    version: str = 'free'  # 'free' or 'pro'


class LicenseManager:

    @property
    def __license_path(self) -> str:
        return f'{pathlib.Path.home()}/.deepl_api_key.json'

    def get_license(self) -> License:
        try:
            with open(self.__license_path, 'r') as license_file:
                file_content: dict[str, str] = json.load(license_file)

                if file_content['key'] and file_content['version']:
                    return License(key=file_content['key'], version=file_content['version'])
                return self.__set_and_get_license()
        except:
            return self.__set_and_get_license()

    def __set_and_get_license(self) -> License:
        self.set_license()
        return self.get_license()

    def set_license(self) -> None:
        with open(self.__license_path, 'w+') as license_file:
            key: str = input('Type here your Deepl API key: ')
            version: str = 'pro' if self.__yes_no_input(
                'Are you using the pro license?') else 'free'
            license: dict[str, str] = {
                'key': key,
                'version': version
            }
            license_file.write(json.dumps(license, indent=2))

    def __yes_no_input(self, question: str) -> bool:
        while True:
            user_input = input(question + " [y/n]: ")
            try:
                return bool(strtobool(user_input))
            except ValueError:
                print("Please use y/n or yes/no.\n")


class DeeplError(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(
            f"\n\n{colorama.Fore.RED}Status code: {status_code}.\nMessage: {message}\n")


class Requester:

    LEN_LIMIT: int = 150

    target_lang: str = ''
    source_lang: str = ''

    __license: License
    __license_manager: LicenseManager = LicenseManager()

    def __init__(self, target_lang: str = '', source_lang: str = '') -> None:
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.__license = self.__license_manager.get_license()

    @property
    def __base_url(self) -> str:
        version: str = '' if self.__license.version == 'pro' else '-free'
        return f'https://api{version}.deepl.com/v2/'

    @property
    def __headers(self) -> dict[str, str]:
        return {
            'Authorization': f'DeepL-Auth-Key {self.__license.key}',
            'Content-Type': 'application/json'
        }

    def __get_usage_info(self) -> Response:
        return requests.get(f'{self.__base_url}usage', headers=self.__headers)

    def print_usage_info(self) -> None:
        response: Response = self.__get_usage_info()

        try:
            body: dict[str, int] = json.loads(response.text)
            character_count: int = body['character_count']
            character_limit: int = body['character_limit']
            percentage: int = round((character_count / character_limit) * 100)
            print_color: str = self.__get_color_by_percentage(percentage)
            print(
                f"\nAPI key: {self.__license.key}.\nCharacters limit: {character_limit}\n{print_color}Used characters: {character_count} ({percentage}%)\n")

        except:
            raise DeeplError(
                status_code=response.status_code,
                message='Error retrieving usage info'
            )

    def __get_color_by_percentage(self, percentage: int) -> str:
        if percentage > 90:
            return colorama.Fore.RED
        if percentage > 60:
            return colorama.Fore.YELLOW
        return colorama.Fore.RESET

    def print_supported_languages(self) -> None:
        response: Response = requests.get(
            f'{self.__base_url}languages', headers=self.__headers)

        try:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        except:
            raise DeeplError(
                status_code=response.status_code,
                message='Error retrieving the supported languages.'
            )

    def translate(self, entry: str) -> str:
        endpoint: str = f"{self.__base_url}translate?auth_key={self.__license.key}&text={entry}&target_lang={self.target_lang}"

        if self.source_lang:
            endpoint += f"&source_lang={self.source_lang}"

        response: Response = requests.get(endpoint)
        truncated_text: str = self.__get_truncated_text(entry)

        try:

            body: dict = json.loads(response.text)
            translation: str = body['translations'][0]['text']

            truncated_translation: str = self.__get_truncated_text(
                translation)
            print(f'"{truncated_text}" => "{truncated_translation}"')
            return translation

        except KeyError:
            print(
                f'{colorama.Fore.YELLOW}\nNo traslation found for "{truncated_text}"!\n')

        except:
            raise DeeplError(
                status_code=response.status_code,
                message=f'Error translating "{truncated_text}".\n'
            )
        finally:
            return ''

    def __get_truncated_text(self, text: str) -> str:
        return text[:self.LEN_LIMIT] + '...' if len(text) > self.LEN_LIMIT else text

    def translate_document(self, source_file: str) -> dict[str, str]:
        request_data: dict[str, str] = {
            'source_lang': self.source_lang,
            'auth_key': self.__license.key,
            'filename': source_file,
        }

        if self.target_lang:
            request_data['target_lang'] = self.target_lang

        endpoint: str = f'{self.__base_url}document/'

        with open(source_file, 'rb') as document:
            response: Response = requests.post(
                endpoint, data=request_data, files={'file': document})

            if response.status_code == 200:
                return json.loads(response.text)

        raise DeeplError(
            status_code=response.status_code,
            message=f'Error translating document "{source_file}"'
        )

    def check_document_status(self, document_id: str, document_key: str) -> dict[str, str]:
        endpoint: str = f'{self.__base_url}document/{document_id}?auth_key={self.__license.key}&document_key={document_key}'
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return json.loads(response.text)

        raise DeeplError(
            status_code=response.status_code,
            message='Error checking the status of a document'
        )

    def download_translated_document(self, document_id: str, document_key: str) -> bytes:
        endpoint: str = f'{self.__base_url}document/{document_id}/result?auth_key={self.__license.key}&document_key={document_key}'
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return response.content

        raise DeeplError(
            status_code=response.status_code,
            message='Error downlaoding a document.'
        )
