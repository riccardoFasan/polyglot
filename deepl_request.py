import requests, json

class DeeplRequest:
    
    KEY = 'fc589597-ab6f-4955-b98f-f6ba8fa80246:fx'
    URL = 'https://api-free.deepl.com/v2/'
    HEADERS = {
        'Authorization' : f'DeepL-Auth-Key {KEY}',
        'Content-Type' : 'application/json'
    }

    def __init__(self, lang):
        self.lang = lang

    def get_usage_info(self):
        response = requests.get(f'{self.URL}usage', headers=self.HEADERS)
        if response.status_code == 200:
            usage_info = json.loads(response.text)
            print(f"\nAuthenticated.\nUsed: {usage_info['character_count']} \nLimit: {usage_info['character_limit']}\n")
        else:
            print(f'\nAuthentication error: {response.status_code}\n')

    def get_translated_word(self, word):
        print(f'Translating: "{word}"...')
        response = requests.get(f'{self.URL}translate?auth_key={self.KEY}&text={word}&target_lang={self.lang}&source_lang=IT')
        if response.status_code == 200:
            try:
                translation = json.loads(response.text)['translations'][0]['text']
                print(f'Found: "{translation}"\n')
                return translation
            except: 
                pass
        print(f'No traslation found\n')
        return ''