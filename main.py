import json, datetime, progressbar
from deepl_request import DeeplRequest

SOURCE = open('./source.json', 'r')

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

data = json.load(SOURCE)
NUMBER_OF_DICTS = get_number_of_dicts(data)

deepl_request = DeeplRequest('BG')  # DE, BG, ES, FR, ES
deepl_request.get_usage_info()

completion_count = 0

with progressbar.ProgressBar(max_value=NUMBER_OF_DICTS, redirect_stdout=True) as bar:

    def translate(dict):
        for key, value in dict.items():
            if isinstance(value, __builtins__.dict):
                translate(value)
            else:
                dict[key] = deepl_request.get_translated_word(value)
                # completion_count +=  1
                # bar.update(completion_count)

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
