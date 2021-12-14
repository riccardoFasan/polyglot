import json, progressbar

class Translation: 

    SOURCE_PATH = './source.json'

    source_dict = dict()
    translations_dict = dict()

    completion_count = 0
    number_of_dicts = 0

    bar = progressbar.ProgressBar(max_value=number_of_dicts, redirect_stdout=True)

    def __init__(self, deepl):
        self.deepl = deepl

    @property
    def destination_path(self):
        return f'./{self.deepl.lang.lower()}.json',

    def translate_source(self):
        self.load_source()
        self.translations_dict = self.source_dict
        self.number_of_dicts = self.get_number_of_dicts(self.source_dict)
        self.bar = progressbar.ProgressBar(max_value=self.number_of_dicts, redirect_stdout=True)
        self.translate(self.translations_dict)
        self.write_translations()

    def load_source(self):
        source = open(self.SOURCE_PATH, 'r')
        self.source_dict = json.load(source) 
        source.close()

    def get_number_of_dicts(self, obj):
        number = 0
        for key, value in obj.items():
            if isinstance(value, dict):
                number += self.get_number_of_dicts(value)
            else:
                number += 1
        return number

    def translate(self, obj):
        for key, value in obj.items():
            if isinstance(value, dict):
                self.translate(value)
            else:
                obj[key] = self.deepl.get_translated_word(value)
                self.completion_count += 1
                self.bar.update(self.completion_count)

    def write_translations(self):
        try:
            destination = open(self.destination_path, 'x')
        except FileExistsError:
            destination = open(self.destination_path, 'w')

        destination.write(json.dumps(self.translations_dict, indent=2))
        destination.close()
