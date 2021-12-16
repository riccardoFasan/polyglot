# DeepL Automation Script

Automation script that, using the [**DeepL API**](https://www.deepl.com/it/docs-api/), generates a **JSON** or a **PO** file from a given source file.

## Usage

There are three available commands: translate, print_usage_data, print_supported_languages. 

### Translate

"Translate" is the main feature of this script. It reads the passed file and creates one or more new files with the translations.

In case of a JSON, it returns a new JSON. In case of a PO file it returns a PO and a MO files. 

#### Command options

| Short-form | Long-form          | Required | Description                                                                                                                                        |
| ---------- | ------------------ | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| -p         | --source_file      | yes      | The JSON or PO file to be translated.                                                                                                              |
| -t         | --target_lang      | yes      | the code of the language into which you want to translate the source file                                                                          |
| -o         | --target_directory | no       | The directory where the output file will be located. Will be used the working directory if this option is invalid or not used.                     |
| -s         | --source_lang      | no       | Source file language code. Detected automatically by DeepL by default. Specifying it can increase performance and make translations more accurate. |

### Basic usage

E.g.: we have a .json source in English and we want to translate it in Italian

```shell
python main.py translate -p en.json -t IT
```

### Advanced usage

E.g.: we have a .po source in English and we want a .po file translated into Japanese with the corresponding .mo file in our house.

```shell
python main.py translate -p en.po -t JA -o $HOME
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


