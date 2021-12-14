from datetime import datetime
from deepl import Deepl
from translation import JSONManager

LANG = 'ES' # DE, BG, ES, FR, ES

START = datetime.now()
print(f'Translator is running.\nScript started at {START}.')

deepl = Deepl(LANG)  
deepl.get_usage_info()

translation_file_manager = JSONManager(deepl)
translation_file_manager.translate_source_file()

END = datetime.now()
print(f'Done.\nScript ended at {END}.\nExecution time: {END - START}.')
