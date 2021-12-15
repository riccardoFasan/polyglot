import os, json, progressbar, polib
from colorama import Fore

class AbstractManager: 

    EXTENSION = ''

    completion_count = 0
    progress_bar = None

    translations_dict = dict()

    def __init__(self, deepl, source_file, target_path=None):
        self.deepl = deepl
        self.source_file = source_file
        self.check_source_file()
        self.target_path = target_path if target_path and os.path.isdir(target_path) else os.getcwd()

    @property
    def target_file(self):
        return f'{self.target_path}/{self.deepl.target_lang.lower()}.{self.EXTENSION}'

    def get_progress_bar(self):
        number_of_translations = self.number_of_translations()
        return progressbar.ProgressBar(max_value=number_of_translations, redirect_stdout=True)

    def check_source_file(self):
        if not os.path.exists(self.source_file):
            print(Fore.RED + f'Error: "{self.source_file}" does not exist!')
            os._exit(0)

    def translate_source_file(self):
        self.load_translations_dict()
        self.progress_bar = self.get_progress_bar()
        self.translate_dict()
        self.write_translations()

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

    def number_of_translations(self, obj=None):
        if obj == None:     
            obj = self.translations_dict
        number = 0
        for key, value in obj.items():
            number += self.number_of_translations(value) if isinstance(value, dict) else  1
        return number

    def load_translations_dict(self):
        pass

    def write_translations(self):
        pass

class JSONManager(AbstractManager):

    EXTENSION = 'json'

    def load_translations_dict(self):
        with open(self.source_file, 'r') as source:
            self.translations_dict = json.load(source) 

    def write_translations(self):
        with open(self.target_file, 'a+') as destination:
            destination.write(json.dumps(self.translations_dict, indent=2))

class PoManager(AbstractManager):

    EXTENSION = 'po'

    def load_translations_dict(self):
        pofile = polib.pofile(self.source_file)
        for entry in pofile:
            self.translations_dict[entry.msgid] = entry.msgstr

    def write_translations(self):
        with open(self.target_file, 'a+') as destination:
            for key, value in self.translations_dict.items():
                destination.write(f'\nmsgid "{key}"\n')
                destination.write(f'msgstr "{value}"\n')
