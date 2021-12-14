from datetime import datetime
from deepl import Deepl
from translation import Translation

LANG = 'DE' # DE, BG, ES, FR, ES

START = datetime.now()
print(f'Translator is running.\nScript started at {START}.')

deepl = Deepl(LANG)  
deepl.get_usage_info()

translation = Translation(deepl)
translation.translate_source()

END = datetime.now()
print(f'Done.\nScript ended at {END}.\nExecution time: {END - START}.')
