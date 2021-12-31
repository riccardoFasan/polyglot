import os
import json
from polib import POEntry, POFile, pofile
from progressbar import ProgressBar
from colorama import Fore

from deeply.deepl import Deepl


class BaseManager:

    source_content: str = ''

    def __init__(self, deepl: Deepl, source_file: str, output_directory: str = None):
        self.source_file = source_file
        self.check_source_file()
        self.deepl = deepl
        self.output_directory = output_directory if output_directory and os.path.isdir(
            output_directory) else os.getcwd()

    @property
    def extension(self):
        name, extension = os.path.splitext(self.source_file)
        return extension

    @property
    def target_file(self):
        return f'{self.output_directory}/{self.deepl.target_lang.lower()}{self.extension}'

    def check_source_file(self):
        if not os.path.exists(self.source_file):
            print(Fore.RED + f'Error: "{self.source_file}" does not exist!')
            os._exit(0)

    def translate_source_file(self):
        self.load_source_content()
        self.translate()
        self.make_translated_files()

    def load_source_content(self):
        try:
            with open(self.source_file, 'r') as source:
                self.source_content = source.read()
        except:
            print(Fore.RED + f'Cannot read {self.extension} files')
            os._exit(0)

    def translate(self):
        self.source_content = self.deepl.translate(self.source_content)

    def make_translated_files(self):
        with open(self.target_file, 'a+') as destination:
            destination.write(self.source_content)
            print(f'\nGenerated {self.target_file}.')


class DictionaryManager(BaseManager):

    completion_count: int = 0
    progress_bar: ProgressBar = None

    source_content: dict = dict()

    def translate_source_file(self):
        self.load_source_content()
        self.progress_bar = self.get_progress_bar()
        self.translate()
        print('\nTranslation completed.')
        self.make_translated_files()

    def get_progress_bar(self):
        number_of_translations: int = self.get_number_of_translations()
        return ProgressBar(max_value=number_of_translations, redirect_stdout=True)

    def get_number_of_translations(self):
        pass


class JSONManager(DictionaryManager):

    def get_number_of_translations(self, obj: dict = None):
        if not obj:
            obj = self.source_content
        number: int = 0
        for key, value in obj.items():
            number += self.get_number_of_translations(
                value) if isinstance(value, dict) else 1
        return number

    def load_source_content(self):
        with open(self.source_file, 'r') as source:
            self.source_content = json.load(source)

    def translate(self, obj=None):
        if not obj:
            obj = self.source_content
        for key, value in obj.items():
            if isinstance(value, dict):
                self.translate(value)
            else:
                obj[key] = self.deepl.translate(value)
                self.completion_count += 1
                self.progress_bar.update(self.completion_count)

    def make_translated_files(self):
        with open(self.target_file, 'a+') as destination:
            destination.write(json.dumps(self.source_content, indent=2))
            print(f'\nGenerated {self.target_file}.')


class POManager(DictionaryManager):

    @property
    def pofile_source(self):
        return pofile(self.source_file)

    def get_number_of_translations(self):
        return len(self.source_content.items())

    def load_source_content(self):
        pofile: POFile = self.pofile_source
        for entry in pofile:
            self.source_content[entry.msgid] = {
                "msgstr": entry.msgid if entry.msgstr == '' else entry.msgstr,
                "occurrences": entry.occurrences
            }

    def translate(self):
        for key, value in self.source_content.items():
            value['msgstr'] = self.deepl.translate(value['msgstr'])
            self.completion_count += 1
            self.progress_bar.update(self.completion_count)

    def make_translated_files(self):
        pofile: POFile = POFile()
        pofile.metadata = self.pofile_source.metadata

        for key, value in self.source_content.items():
            entry: POEntry = POEntry(
                msgid=key,
                msgstr=value["msgstr"],
                occurrences=value['occurrences']
            )
            pofile.append(entry)

        pofile.save(self.target_file)

        mofile: str = f'{self.output_directory}/{self.deepl.target_lang.lower()}.mo'
        pofile.save_as_mofile(mofile)
        print(f'\nGenerated {self.target_file} and {mofile}.')
