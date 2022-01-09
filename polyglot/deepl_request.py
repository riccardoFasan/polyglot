import requests
import json
import os
from colorama import Fore
from pathlib import Path
from requests.models import Response


class DeeplRequest:

    LEN_LIMIT: int = 150
    license: dict = {
        'version': 'free',  # 'free', 'pro' or 'invalid'
        'key': ''
    }

    def __init__(self, target_lang: str = None, source_lang: str = None):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.apply_license()

    @property
    def base_url(self):
        version: str = '' if self.license['version'] == 'pro' else '-free'
        return f'https://api{version}.deepl.com/v2/'

    @property
    def license_path(self):
        return f'{Path.home()}/.deepl_api_key.json'

    @property
    def headers(self):
        return {
            'Authorization': f'DeepL-Auth-Key {self.license["key"]}',
            'Content-Type': 'application/json'
        }

    def apply_license(self):
        try:
            with open(self.license_path, 'r') as license_file:
                file_content: dict = json.load(license_file)

                if file_content['key'] and file_content['version']:
                    self.license['key'] = file_content['key']
                    self.license['version'] = file_content['version']

        except:
            self.set_key()

    def set_key(self):
        with open(self.license_path, 'w+') as license_file:
            self.license['key'] = input('Type here your Deepl API key: ')
            self.license['version'] = self.get_key_version()
            self.verify_license()
            license: dict = {
                'key': self.license['key'],
                'version': self.license['version']
            }
            license_file.write(json.dumps(license, indent=2))

    def get_key_version(self):
        response: Response = self.get_usage_info()
        if response.status_code == 403:
            if self.license['version'] == 'free':
                self.license['version'] = 'pro'
                self.get_key_version()
            return 'invalid'
        return self.license['version']

    def verify_license(self):
        if self.license['version'] == 'invalid':
            print(f'{Fore.RED}\nThis key is invalid.\n')
            os._exit(0)

    def get_usage_info(self):
        return requests.get(f'{self.base_url}usage', headers=self.headers)

    def print_usage_info(self):
        response: Response = self.get_usage_info()

        if response.status_code == 200:
            body: dict = json.loads(response.text)
            character_count: int = body['character_count']
            character_limit: int = body['character_limit']
            percentage: int = round((character_count / character_limit) * 100)
            print_color: str = self.get_color_by_percentage(percentage)
            print(
                f"\nAPI key: {self.license['key']}.\nCharacters limit: {character_limit}\n{print_color}Used characters: {character_count} ({percentage}%)\n")

        else:
            print(
                f"{Fore.RED}\nError retrieving usage info.\nError code: {response.status_code}.\n")

    def get_color_by_percentage(self, percentage: int):
        if percentage > 90:
            return Fore.RED
        if percentage > 60:
            return Fore.YELLOW
        return Fore.RESET

    def print_supported_languages(self):
        response: Response = requests.get(
            f'{self.base_url}languages', headers=self.headers)

        if response.status_code == 200:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        else:
            print(
                f'{Fore.RED}\nError retrieving the supported languages.\nError code: {response.status_code}\n')

    def translate(self, entry: str):
        endpoint: str = f"{self.base_url}translate?auth_key={self.license['key']}&text={entry}&target_lang={self.target_lang}"

        if self.source_lang:
            endpoint += f"&source_lang={self.source_lang}"

        response: Response = requests.get(endpoint)
        truncated_text: str = self.get_truncated_text(entry)

        if response.status_code == 200:
            body: dict = json.loads(response.text)
            translation: str | None = self.get_translation(body)

            if translation:
                truncated_translation: str = self.get_truncated_text(
                    translation)
                print(f'"{truncated_text}" => "{truncated_translation}"')
                return translation

            print(
                f'{Fore.YELLOW}\nNo traslation found for "{truncated_text}"!\n')

        else:
            print(
                f'{Fore.RED}\nError translating "{truncated_text}".\nError code: {response.status_code}.\n')

        return ''

    def get_translation(self, body: dict):
        try:
            return body['translations'][0]['text']
        except:
            return None

    def get_truncated_text(self, text: str):
        return text[:self.LEN_LIMIT] + '...' if len(text) > self.LEN_LIMIT else text

    def translate_document(self, source_file: str):
        request_data: dict = {
            'source_lang': self.source_lang,
            'auth_key': self.license['key'],
            'filename': source_file,
        }

        if self.target_lang:
            request_data['target_lang'] = self.target_lang

        endpoint: str = f'{self.base_url}document/'

        with open(source_file, 'rb') as document:
            response: Response = requests.post(
                endpoint, data=request_data, files={'file': document})

            if response.status_code == 200:
                return json.loads(response.text)

        print(
            f'{Fore.RED}\nError translating "{source_file}".\nError code: {response.status_code}.\n')
        os._exit(0)

    def check_document_status(self, document_id: str, document_key: str):
        endpoint: str = f'{self.base_url}document/{document_id}?auth_key={self.license["key"]}&document_key={document_key}'
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return json.loads(response.text)

        print(f'{Fore.RED}\nError checking the status of a document\nError code: {response.status_code}.\n')
        os._exit(0)

    def download_translated_document(self, document_id: str, document_key: str):
        endpoint: str = f'{self.base_url}document/{document_id}/result?auth_key={self.license["key"]}&document_key={document_key}'
        response: Response = requests.post(endpoint)

        if response.status_code == 200:
            return response.content

        print(
            f'{Fore.RED}\nError downlaoding a document\nError code: {response.status_code}.\n')
        os._exit(0)
