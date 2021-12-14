import requests, json, datetime, progressbar

KEY = 'fc589597-ab6f-4955-b98f-f6ba8fa80246:fx'
URL = 'https://api-free.deepl.com/v2/'
HEADERS = {
    'Authorization' : f'DeepL-Auth-Key {KEY}',
    'Content-Type' : 'application/json'
}

LANG = 'BG' # DE, BG, ES, FR, ES

SOURCE = open('./source.json', 'r')

def get_usage_info():
    response = requests.get(f'{URL}usage', headers=HEADERS)
    if response.status_code == 200:
        usage_info = json.loads(response.text)
        print(f"\nAuthenticated.\nUsed: {usage_info['character_count']} \nLimit: {usage_info['character_limit']}\n")
    else:
        print(f'\nAuthentication error: {response.status_code}\n')

def api_call(word):
    print(f'Translating: "{word}"...')
    response = requests.get(f'{URL}translate?auth_key={KEY}&text={word}&target_lang={LANG}&source_lang=IT')
    if response.status_code == 200:
        try:
            translation = json.loads(response.text)['translations'][0]['text']
            print(f'Found: "{translation}"\n')
            return translation
        except: 
            pass
    print(f'No traslation found\n')
    return ''

def get_number_of_dicts(dict):
    number = 0
    for key, value in dict.items():
        if isinstance(value, __builtins__.dict):
            number += get_number_of_dicts(value)
        else:
            number += 1
    return number

START = datetime.datetime.now()
print(f'Translator is running.\nScript started at {START}.')

get_usage_info()
data = json.load(SOURCE)

NUMBER_OF_DICTS = get_number_of_dicts(data)
completion_count = 0

with progressbar.ProgressBar(max_value=NUMBER_OF_DICTS, redirect_stdout=True) as bar:

    def translate(dict):
        for key, value in dict.items():
            if isinstance(value, __builtins__.dict):
                translate(value)
            else:
                dict[key] = api_call(value)
                completion_count += 1
                bar.update(completion_count)

    translate(data)

try:
    DESTINATION = open(f'./{LANG.lower()}.json', 'x')
except FileExistsError:
    DESTINATION = open(f'./{LANG.lower()}.json', 'w')

DESTINATION.write(json.dumps(data, indent=2))

SOURCE.close()
DESTINATION.close()

END = datetime.datetime.now()
print(f'Done.\nScript ended at {END}.\nExecution time: {END - START}.')
