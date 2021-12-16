# DeepL Automation Script

Automation script that, using the [**DeepL API**](https://www.deepl.com/it/docs-api/), generates a **JSON** or a **PO** file from a given source file.

## Usage

There are three available commands: translate, print_usage_data, print_supported_languages. 

### Translate

"Translate" is the main feature of this script. It takes and reads the passed file and creates one or more files with the translations.

In case of a JSON, it returns a new JSON. In case of a PO file it returns a PO and a MO files. 

#### Basic usage

Basic usage with a json file (we want a json with the Italian translations from a source in English):

```shell
python main.py translate -p en.json -t IT
```

### Print usage data

It returns DeepL usage info related to your API key, run with: 

```shell
python main.py print_usage_data
```

### Print supported languages

It returns the list of languages currently supported by DeepL, run with:

```shell
python main.py print_supported_languages
```

## Dependencies

- [Colorama](https://github.com/tartley/colorama)

- [Progressbar 2](https://github.com/WoLpH/python-progressbar)

- [Polib](https://github.com/izimobil/polib/)
