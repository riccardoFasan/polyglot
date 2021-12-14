import json, progressbar

class TranslationManager: 

    SOURCE_PATH = './source.json'

    translations_dict = dict()
    completion_count = 0
    progress_bar = None

    def __init__(self, deepl):
        self.deepl = deepl

    @property
    def destination_path(self):
        return f'./{self.deepl.lang.lower()}.json'

    def get_destination_file(self):
        try:
            return open(self.destination_path, 'x')
        except FileExistsError:
            return open(self.destination_path, 'w')

    def get_progress_bar(self):
        number_of_dicts = self.get_number_of_dicts()
        return progressbar.ProgressBar(max_value=number_of_dicts, redirect_stdout=True)

    def translate_source_file(self):
        self.load_source()
        self.progress_bar = self.get_progress_bar()

    def load_source(self):
        source = open(self.SOURCE_PATH, 'r')
        self.translations_dict = json.load(source) 
        source.close()

class JSONManager(TranslationManager):

    def translate_source_file(self):
        super().translate_source_file()
        self.translate_dict()
        self.write_translations()

    def get_number_of_dicts(self, obj=None):
        if obj == None:     
            obj = self.translations_dict
        number = 0
        for key, value in obj.items():
            number += self.get_number_of_dicts(value) if isinstance(value, dict) else  1
        return number

    def translate_dict(self, obj=None):
        if obj == None: 
            obj = self.translations_dict
        for key, value in obj.items():
            if isinstance(value, dict):
                self.translate_dict(value)
            else:
                obj[key] = self.deepl.get_translated_word(value)
                self.completion_count += 1
                self.progress_bar.update(self.completion_count)

    def write_translations(self):
        destination = self.get_destination_file()
        destination.write(json.dumps(self.translations_dict, indent=2))
        destination.close()
