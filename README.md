# Deeply - Automate translations with DeepL

Deeply is a CLI tool that automates translations tasks.
Using the [**DeepL API**](https://www.deepl.com/it/docs-api/), Deeply generates a translated file from a given source file. 

Deeply is born to translate **JSON** and **PO** files, but it supports even **common text files**, like .txt.

## Installation

Install [Python](https://www.python.org/) if you haven't already done so, then use **pip** to install Deeply.

```shell
pip install deeply-translator
```

Then you can run Deeply by running:

```shell
python -m deeply
```

And that's all.

Soon the whole script will be packaged for other package managers like pacman, apt and brew.

### Optional

I suggest you to update your PATH in order to call the command faster.

```shell
export PATH=$PATH:$HOME/.local/bin
```

Now you can run deeply simply with: 

```shell
deeply
```

## Usage

There are three available commands: translate, print_usage_data and print_supported_languages. 

### Translate

"Translate" is the main feature of Deeply. It reads the passed file and creates one or more new files with the translations. It creates a new file with the translations and doesn't edit the source file. 

> ℹ️ In the case of a PO file, it returns both a PO and an MO file.

#### Command options

| Option                 | Required | Description                                                                                                                                        |
|:---------------------- |:-------- |:-------------------------------------------------------------------------------------------------------------------------------------------------- |
| -p, --source_file      | yes      | The JSON or PO file to be translated.                                                                                                              |
| -t, --target_lang      | yes      | the code of the language into which you want to translate the source file                                                                          |
| -o, --output_directory | no       | The directory where the output file will be located. **Will be used the working directory if this option is invalid or not used**.                 |
| -s, --source_lang      | no       | Source file language code. Detected automatically by DeepL by default. Specifying it can increase performance and make translations more accurate. |

#### Basic usage

E.g.: we have a .json source in English and we want to translate it in Italian.

```shell
deeply translate -p en.json -t IT
```

#### Advanced usage

E.g.: we have a .po source in English and we want a .po file translated into Japanese with the corresponding .mo file in our home. We specify the source language to benefit DeepL.

```shell
deeply translate -p en.po -t JA -o $HOME -s EN
```

### Print usage data

It returns DeepL usage info related to your API key, run with: 

```shell
deeply print_usage_data
```

### Print supported languages

It returns the list of languages currently supported by DeepL, run with:

```shell
deeply print_supported_languages
```

## Dependencies

- [Colorama](https://github.com/tartley/colorama)

- [Progressbar 2](https://github.com/WoLpH/python-progressbar)

- [Polib](https://github.com/izimobil/polib/)