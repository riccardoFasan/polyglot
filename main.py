import requests, json

KEY = 'fc589597-ab6f-4955-b98f-f6ba8fa80246:fx'
URL = 'https://api-free.deepl.com/v2/'
HEADERS = {
    'Authorization' : f'DeepL-Auth-Key {KEY}',
    'Content-Type' : 'application/json'
}

LANG = 'EN' # DE, BG, ES, FR

SOURCE = open('./source.json', 'r')
DESTINATION = open('./destination.json', 'w')

def get_usage_info():
    response = requests.get(f'{URL}usage', headers=HEADERS)
    if response.status_code == 200:
        usage_info = json.loads(response.text)
        print(f"Authenticated.\nUsed: {usage_info['character_count']} \nLimit: {usage_info['character_limit']}\n")
    else:
        print(f'Authentication error: {response.status_code}')


def api_call(word):
    response = requests.get(f'{URL}translate?auth_key={KEY}&text={word}&target_lang={LANG}&source_lang=IT')
    if response.status_code == 200:
        try:
            return json.loads(response.text)['translations'][0]['text']
        except: 
            pass
    return ''

get_usage_info()

def translate(dict):
    for key, value in dict.items():
        if isinstance(value, __builtins__.dict):
            translate(value)
        else:
            dict[key] = api_call(value)

data = json.load(SOURCE)
translate(data)

DESTINATION.write(json.dumps(data, indent=2))

SOURCE.close()
DESTINATION.close()

