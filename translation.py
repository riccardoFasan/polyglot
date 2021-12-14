import os, json, progressbar
from colorama import Fore

class TranslationManager: 

    translations_dict = dict()
    completion_count = 0
    progress_bar = None

    def __init__(self, deepl, source_file, target_path=None):
        self.deepl = deepl
        self.source_file = source_file
        self.check_source_file()
        self.target_path = target_path if target_path and os.path.isdir(target_path) else os.getcwd()

    def check_source_file(self):
        if not os.path.exists(self.source_file):
            print(Fore.RED + f'Error: "{self.source_file}" does not exist!')
            os._exit(0)

    def get_destination_file(self):
        try:
            return open(self.target_file, 'x')
        except FileExistsError:
            return open(self.target_file, 'w')

    @property
    def target_file(self):
        return f'./{self.deepl.lang.lower()}.json'

    def translate_source_file(self):
        self.load_source()
        self.progress_bar = self.get_progress_bar()

    def load_source(self):
        source = open(self.source_file, 'r')
        self.translations_dict = json.load(source) 
        source.close()

    def get_progress_bar(self):
        number_of_dicts = self.get_number_of_dicts()
        return progressbar.ProgressBar(max_value=number_of_dicts, redirect_stdout=True)

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


# TODO: POManager