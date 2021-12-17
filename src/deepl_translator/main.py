import argparse, os
from colorama import init, Fore

from deepl import Deepl
from managers import JSONManager, PoManager

init()

def translate(args):
    deepl = Deepl(args.target_lang, args.source_lang)  
    
    name, extension = os.path.splitext(args.source_file)

    if extension == '.json':
        manager = JSONManager(deepl, args.source_file, args.target_directory)
    elif extension == '.po':
        manager = PoManager(deepl, args.source_file, args.target_directory)
    else:
        print(Fore.RED + f'No manager for {extension} files')
        os._exit(0)

    manager.translate_source_file()
    
    print(Fore.GREEN + f'\nFinish.\n')

def print_data_or_translate(args):
    if args.action == 'translate':
        translate(args)
    else:
        deepl = Deepl()
        if args.action == 'print_supported_languages':
            deepl.print_supported_languages()
        elif args.action == 'print_usage_info':
            deepl.print_usage_info()
        else:
            print(Fore.RED + f"No action selected.")
    
ACTIONS = [ 'translate', 'print_supported_languages', 'print_usage_info']

parser = argparse.ArgumentParser(description='Using the DeepL API, this script translate the given json or po file')

parser.add_argument('action', type=str, help="The action that will be exectued.", choices=ACTIONS)
parser.add_argument('-p', '--source_file', type=str, help='The JSON or PO file to be translated. Required if the action is "translate"', default=None)
parser.add_argument('-t', '--target_lang', type=str, help='the code of the language into which you want to translate the source file. Required if the action is "translate"', default=None)
parser.add_argument('-o', '--target_directory', type=str, help='The directory where the output file will be located. Will be used the working directory if this option is invalid or not used.', default=None)
parser.add_argument('-s', '--source_lang', type=str, help='Source file language code. Detected automatically by DeepL by default. Specifying it can increase performance and make translations more accurate.', default=None)

args = parser.parse_args()

if args.action == 'translate' and (args.source_file is None or args.target_lang is None):
    parser.error("translate requires --source_file and --target_lang.")

print_data_or_translate(args)