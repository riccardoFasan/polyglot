import requests, json

class Deepl:
    
    KEY = 'fc589597-ab6f-4955-b98f-f6ba8fa80246:fx'
    URL = 'https://api-free.deepl.com/v2/'
    HEADERS = {
        'Authorization' : f'DeepL-Auth-Key {KEY}',
        'Content-Type' : 'application/json'
    }

    def __init__(self, target_lang=None, source_lang=None):
        self.target_lang = target_lang
        self.source_lang = source_lang

    def print_usage_info(self):
        response = requests.get(f'{self.URL}usage', headers=self.HEADERS)
        if response.status_code == 200:
            body = json.loads(response.text)
            print(f"\nAPI key: {self.KEY}.\nUsed characters: {body['character_count']} \nCharacters limit: {body['character_limit']}\n")
        else:
            print(f"\nError retrieving usage info: {response.status_code}\n")

    def print_supported_languages(self):
        response = requests.get(f'{self.URL}languages', headers=self.HEADERS)
        if response.status_code == 200:
            body = json.loads(response.text)
            for lang in body:
                print(f"{lang['name']} ({lang['language']})")
        else:
            print(f'\Error retrieving the supported languages: {response.status_code}\n')

    def get_translated_word(self, word):
        endpoint = f"{self.URL}translate?auth_key={self.KEY}&text={word}&target_lang={self.target_lang}"
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