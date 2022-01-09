import requests
import json
from colorama import Fore
from pathlib import Path
from requests.models import Response


class DeeplRequest:

    BASE_URL: str = 'https://api-free.deepl.com/v2/'
    LEN_LIMIT: int = 150

    def __init__(self, target_lang: str = None, source_lang: str = None):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.key = self.get_or_ask_key()

    @property
    def key_path(self):
        return f'{Path.home()}/.deepl_api_key.txt'

    @property
    def headers(self):
        return {
            'Authorization': f'DeepL-Auth-Key {self.key}',
            'Content-Type': 'application/json'
        }

    def get_or_ask_key(self):
        with open(self.key_path, 'a+') as key_file:
            key_file.seek(0)  #  Nosense, but OK
            key: str = key_file.read()

            if key == '':
                key = input('Type here your Deepl API key: ')
                key_file.write(key)

            return key

    def set_key(self):
        with open(self.key_path, 'w+') as key_file:
            key = input('Type here your Deepl API key: ')
            key_file.write(key)

    def print_usage_info(self):
        response: Response = requests.get(
            f'{self.BASE_URL}usage', headers=self.headers)

        if response.status_code == 200:
            body: dict = json.loads(response.text)
            character_count: int = body['character_count']
            character_limit: int = body['character_limit']
            percentage: int = round((character_count / character_limit) * 100)
            print(
                f"\nAPI key: {self.key}.\nCharacters limit: {character_limit}")
            print_color: str = self.get_color_by_percentage(percentage)
            print(
                print_color + f"Used characters: {character_count} ({percentage}%)", Fore.RESET + f'\n')

        else:
            print(Fore.RED + f"\nError retrieving usage info.",
                  f'Error code: {response.status_code}.', Fore.RESET + f'\n')

    def get_color_by_percentage(self, percentage: int):
        if percentage > 90:
            return Fore.RED
        if percentage > 60:
            return Fore.YELLOW
        return Fore.RESET

    def print_supported_languages(self):
        response: Response = requests.get(
            f'{self.BASE_URL}languages', headers=self.headers)

        if response.status_code == 200:
            body: dict = json.loads(response.text)

            for lang in body:
                print(f"{lang['name']} ({lang['language']})")

        else:
            print(Fore.RED + f'\Error retrieving the supported languages.',
                  f'Error code: {response.status_code}.', Fore.RESET + f'\n')

    def translate(self, entry: str):
        endpoint: str = f"{self.BASE_URL}translate?auth_key={self.key}&text={entry}&target_lang={self.target_lang}"

        if self.source_lang:
            endpoint += f"&source_lang={self.source_lang}"

        response: Response = requests.get(endpoint)
        body: dict = json.loads(response.text)
        truncated_text: str = self.get_truncated_text(entry)

        if response.status_code == 200:

            translation: str | None = self.get_translation(body)

            if translation:
                truncated_translation: str = self.get_truncated_text(
                    translation)
                print(f'"{truncated_text}" => "{truncated_translation}"')
                return translation

            # Writing this 2 print in one line causes an error and it prints nothing. No idea why.
            print(Fore.YELLOW + f'\n')
            print(
                f'No traslation found for "{truncated_text}"!', Fore.RESET + f'\n')

        else:
            message: str = body['message']
            print(Fore.RED + f'\nError translating "{truncated_text}".\n\n',
                  f'Error code: {response.status_code}.\n', f'Error message: {message}', Fore.RESET + f'\n')

        return None

    def get_translation(self, body: dict):
        try:
            return body['translations'][0]['text']
        except:
            return None

    def get_truncated_text(self, text: str):
        return text[:self.LEN_LIMIT] + '...' if len(text) > self.LEN_LIMIT else text
