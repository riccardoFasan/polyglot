import requests, json
from colorama import Fore
from pathlib import Path

class Deepl:

    BASE_URL = 'https://api-free.deepl.com/v2/'

    def __init__(self, target_lang=None, source_lang=None):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.key = self.get_or_ask_key()

    @property
    def key_path(self):
        return f'{Path.home()}/.deepl_api_key.txt'

    @property
    def headers(self):
            return {
            'Authorization' : f'DeepL-Auth-Key {self.key}',
            'Content-Type' : 'application/json'
        }

    def get_or_ask_key(self):
        with open(self.key_path, 'a+') as key_file:
            key_file.seek(0) # Nosense, but OK
            key = key_file.read()
            if key == '':
                key = input('Type here your Deepl API key: ')
                key_file.write(key)
            return key

    def print_usage_info(self):
        response = requests.get(f'{self.BASE_URL}usage', headers=self.headers)
        if response.status_code == 200:
            body = json.loads(response.text)
            print(f"\nAPI key: {self.key}.\nUsed characters: {body['character_count']} \nCharacters limit: {body['character_limit']}\n")
        else:
            print(Fore.RED + f"\nError retrieving usage info.", f'Error code: {response.status_code}.', Fore.RESET + f'\n')

    def print_supported_languages(self):
        response = requests.get(f'{self.BASE_URL}languages', headers=self.headers)
        if response.status_code == 200:
            body = json.loads(response.text)
            for lang in body:
                print(f"{lang['name']} ({lang['language']})")
        else:
            print(Fore.RED + f'\Error retrieving the supported languages.', f'Error code: {response.status_code}.', Fore.RESET + f'\n')

    def get_translated_word(self, word):
        endpoint = f"{self.BASE_URL}translate?auth_key={self.key}&text={word}&target_lang={self.target_lang}"
        if self.source_lang: 
            endpoint += f"&source_lang={self.source_lang}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            try:
                translation = json.loads(response.text)['translations'][0]['text']
                print(f'"{word}" => {translation}"')
                return translation
            except: 
                print(Fore.YELLOW + f'\nNo traslation found for "{word}"!', Fore.RESET + f'')
        else:
            print(Fore.RED + f'\nError translating "{word}".', f'Error code: {response.status_code}.', Fore.RESET + f'\n')
        return ''
