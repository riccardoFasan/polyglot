import requests, json
from colorama import Fore

class Deepl:

    BASE_URL = 'https://api-free.deepl.com/v2/'
    KEY_PATH = './api_key.txt'

    def __init__(self, target_lang=None, source_lang=None):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.key = self.get_api_key()

    def get_api_key(self):
        with open(self.KEY_PATH, 'a+') as key_file:
            key_file.seek(0) # Nosense, but OK
            key = key_file.read()
            if key == '':
                key = input('Type here your Deepl API key:')
                key_file.write(key)
            return key

    @property
    def headers(self):
            return {
            'Authorization' : f'DeepL-Auth-Key {self.key}',
            'Content-Type' : 'application/json'
        }

    def print_usage_info(self):
        response = requests.get(f'{self.BASE_URL}usage', headers=self.headers)
        if response.status_code == 200:
            body = json.loads(response.text)
            print(f"\nAPI key: {self.key}.\nUsed characters: {body['character_count']} \nCharacters limit: {body['character_limit']}\n")
        else:
            print(Fore.Red + f"\nError retrieving usage info: {response.status_code}\n")

    def print_supported_languages(self):
        response = requests.get(f'{self.BASE_URL}languages', headers=self.headers)
        if response.status_code == 200:
            body = json.loads(response.text)
            for lang in body:
                print(f"{lang['name']} ({lang['language']})")
        else:
            print(Fore.Red + f'\Error retrieving the supported languages: {response.status_code}\n')

    def get_translated_word(self, word):
        endpoint = f"{self.BASE_URL}translate?auth_key={self.KEY}&text={word}&target_lang={self.target_lang}"
        if self.source_lang: 
            endpoint += f"&source_lang={self.source_lang}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            try:
                translation = json.loads(response.text)['translations'][0]['text']
                print(f'Translation found: "{word}" => {translation}"')
                return translation
            except: 
                pass
        print(f'No traslation found for "{word}"!')
        return ''
