import requests
import json
import os
import pathlib
import colorama
from requests.models import Response


class DeeplRequest:

    LEN_LIMIT: int = 150
    license: dict[str, str] = {
        'version': 'free',  # 'free', 'pro' or 'invalid'
        'key': ''
    }

    target_lang: str = ''
    source_lang: str = ''

    def __init__(self, target_lang: str = '', source_lang: str = '') -> None:
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.__apply_license()

    @property
    def __base_url(self) -> str:
        version: str = '' if self.license['version'] == 'pro' else '-free'
        return f'https://api{version}.deepl.com/v2/'

    @property
    def __license_path(self) -> str:
        return f'{pathlib.Path.home()}/.deepl_api_key.json'

    @property
    def __headers(self) -> dict[str, str]:
        return {
            'Authorization': f'DeepL-Auth-Key {self.license["key"]}',
            'Content-Type': 'application/json'
        }

    def __apply_license(self) -> None:
        try:

            with open(self.__license_path, 'r') as license_file:
                file_content: dict[str, str] = json.load(license_file)

                if file_content['key'] and file_content['version']:
                    self.license['key'] = file_content['key']
                    self.license['version'] = file_content['version']

        except:
            self.set_key()

    def set_key(self) -> None:
        with open(self.__license_path, 'w+') as license_file:
            self.license['key'] = input('Type here your Deepl API key: ')
            self.license['version'] = self.__get_key_version()
            self.__verify_license()
            license: dict[str, str] = {
                'key': self.license['key'],
                'version': self.license['version']
            }
            license_file.write(json.dumps(license, indent=2))

    def __get_key_version(self) -> str:
        response: Response = self.__get_usage_info()
        if response.status_code == 403:
            if self.license['version'] == 'free':
                self.license['version'] = 'pro'
                self.__get_key_version()
            return 'invalid'
        return self.license['version']

    def __verify_license(self):
        if self.license['version'] == 'invalid':
            print(f'{colorama.Fore.RED}\nThis key is invalid.\n')
            os._exit(0)

    def __get_usage_info(self) -> Response:
        return requests.get(f'{self.__base_url}usage', headers=self.__headers)

    def print_usage_info(self) -> None:
        response: Response = self.__get_usage_info()

        if response.status_code == 200:
            body: dict[str, int] = json.loads(response.text)
            character_count: int = body['character_count']
            character_limit: int = body['character_limit']
            percentage: int = round((character_count / character_limit) * 100)
            print_color: str = self.__get_color_by_percentage(percentage)
            print(
                f"\nAPI key: {self.license['key']}.\nCharacters limit: {character_limit}\n{print_color}Used characters: {character_count} ({percentage}%)\n")

        else:
            print(
                f"{colorama.Fore.RED}\nError retrieving usage info.\nError code: {response.status_code}.\n")

    def __get_color_by_percentage(self, percentage: int) -> str:
        if percentage > 90:
            return colorama.Fore.RED
        if percentage > 60:
            return colorama.Fore.YELLOW
        return colorama.Fore.RESET

    def print_supported_languages(self) -> None:
        response: Response = requests.get(
            f'{self.__base_url}languages', headers=self.__headers)

        if response.status_code == 200:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        else:
            print(
                f'{colorama.Fore.RED}\nError retrieving the supported languages.\nError code: {response.status_code}\n')

    def translate(self, entry: str) -> str:
        endpoint: str = f"{self.__base_url}translate?auth_key={self.license['key']}&text={entry}&target_lang={self.target_lang}"

        if self.source_lang:
            endpoint += f"&source_lang={self.source_lang}"

        response: Response = requests.get(endpoint)
        truncated_text: str = self.__get_truncated_text(entry)

        if response.status_code == 200:
            body: dict[str, str] = json.loads(response.text)
            translation: str | None = self.__get_translation(body)

            if translation:
                truncated_translation: str = self.__get_truncated_text(
                    translation)
                print(f'"{truncated_text}" => "{truncated_translation}"')
                return translation

            print(
                f'{colorama.Fore.YELLOW}\nNo traslation found for "{truncated_text}"!\n')

        else:
            print(
                f'{colorama.Fore.RED}\nError translating "{truncated_text}".\nError code: {response.status_code}.\n')

        return ''

    def __get_translation(self, body: dict) -> str | None:
        try:
            return body['translations'][0]['text']
        except:
            return None

    def __get_truncated_text(self, text: str) -> str:
        return text[:self.LEN_LIMIT] + '...' if len(text) > self.LEN_LIMIT else text

    def translate_document(self, source_file: str) -> dict[str, str]:
        request_data: dict[str, str] = {
            'source_lang': self.source_lang,
            'auth_key': self.license['key'],
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

        print(
            f'{colorama.Fore.RED}\nError translating "{source_file}".\nError code: {response.status_code}.\n')
        os._exit(0)

    def check_document_status(self, document_id: str, document_key: str) -> dict[str, str]:
        endpoint: str = f'{self.__base_url}document/{document_id}?auth_key={self.license["key"]}&document_key={document_key}'
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return json.loads(response.text)

        print(f'{colorama.Fore.RED}\nError checking the status of a document\nError code: {response.status_code}.\n')
        os._exit(0)

    def download_translated_document(self, document_id: str, document_key: str) -> bytes:
        endpoint: str = f'{self.__base_url}document/{document_id}/result?auth_key={self.license["key"]}&document_key={document_key}'
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return response.content

        print(
            f'{colorama.Fore.RED}\nError downlaoding a document\nError code: {response.status_code}.\n')
        os._exit(0)
