import os, json, progressbar, polib
from colorama import Fore

class AbstractManager: 

    EXTENSION = ''

    completion_count = 0
    progress_bar = None

    translations_dict = dict()

    def __init__(self, deepl, source_file, target_directory=None):
        self.deepl = deepl
        self.source_file = source_file
        self.check_source_file()
        self.target_directory = target_directory if target_directory and os.path.isdir(target_directory) else os.getcwd()

    @property
    def target_file(self):
        return f'{self.target_directory}/{self.deepl.target_lang.lower()}.{self.EXTENSION}'

    def get_progress_bar(self):
        number_of_translations = self.get_number_of_translations()
        return progressbar.ProgressBar(max_value=number_of_translations, redirect_stdout=True)

    def check_source_file(self):
        if not os.path.exists(self.source_file):
            print(Fore.RED + f'Error: "{self.source_file}" does not exist!')
            os._exit(0)

    def translate_source_file(self):
        self.load_translations_dict()
        self.progress_bar = self.get_progress_bar()
        self.translate_dict()
        self.progress_bar = None
        self.make_translated_files()
        print('\nTranslation completed.')

    def get_number_of_translations(self):
        pass

    def load_translations_dict(self):
        pass

    def translate_dict(self):
        pass

    def make_translated_files(self):
        pass

class JSONManager(AbstractManager):

    EXTENSION = 'json'

    def get_number_of_translations(self, obj=None):
        if not obj:     
            obj = self.translations_dict
        number = 0
        for key, value in obj.items():
            number += self.get_number_of_translations(value) if isinstance(value, dict) else  1
        return number

    def load_translations_dict(self):
        with open(self.source_file, 'r') as source:
            self.translations_dict = json.load(source) 

    def translate_dict(self, obj=None):
        if not obj: 
            obj = self.translations_dict
        for key, value in obj.items():
            if isinstance(value, dict):
                self.translate_dict(value)
            else:
                obj[key] = self.deepl.get_translated_word(value)
                self.completion_count += 1
                self.progress_bar.update(self.completion_count)

    def make_translated_files(self):
        with open(self.target_file, 'a+') as destination:
            destination.write(json.dumps(self.translations_dict, indent=2))
            print(f'\nGenerated {self.target_file}.')

class PoManager(AbstractManager):

    EXTENSION = 'po'

    @property
    def pofile_source(self):
        return polib.pofile(self.source_file)

    def get_number_of_translations(self):
        return len(self.translations_dict.items())

    def load_translations_dict(self):
        pofile = self.pofile_source
        for entry in pofile:
            self.translations_dict[entry.msgid] = { 
                "msgstr" : entry.msgstr,
                "occurrences" : entry.occurrences   
            }

    def translate_dict(self):
        for key, value in self.translations_dict.items():
            value['msgstr'] = self.deepl.get_translated_word(value['msgstr'])
            self.completion_count += 1
            self.progress_bar.update(self.completion_count)

    def make_translated_files(self):
        pofile = polib.POFile()
        pofile.metadata = self.pofile_source.metadata

        for key, value in self.translations_dict.items():
            entry = polib.POEntry(
                msgid = key,
                msgstr = value["msgstr"],
                occurrences = value['occurrences']
            )
            pofile.append(entry)

        pofile.save(self.target_file)

        mofile = f'{self.target_directory}/{self.deepl.target_lang.lower()}.mo'
        pofile.save_as_mofile(mofile)
        print(f'\nGenerated {self.target_file} and {mofile}.')
