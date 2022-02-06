import json, pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from distutils.util import strtobool


@dataclass
class License:
    key: str = ''
    version: str = 'free'  # 'free' or 'pro'


class LicenseManager(ABC):

    @abstractmethod
    def get_license(self) -> License:
        return License(key='', version='')

    @abstractmethod
    def set_license(self) -> None:
        pass

class CLILicenseManager(LicenseManager):

    @property
    def __license_path(self) -> str:
        return f'{pathlib.Path.home()}/.deepl_api_key.json'

    def get_license(self) -> License:
        try:
            with open(self.__license_path, 'r') as license_file:
                file_content: dict[str, str] = json.load(license_file)

                if file_content['key'] and file_content['version']:
                    return License(key=file_content['key'], version=file_content['version'])
                return self.__set_and_get_license()
        except:
            return self.__set_and_get_license()

    def __set_and_get_license(self) -> License:
        self.set_license()
        return self.get_license()

    def set_license(self) -> None:
        with open(self.__license_path, 'w+') as license_file:
            key: str = input('Type here your Deepl API key: ')
            version: str = 'pro' if self.__yes_no_input(
                'Are you using the pro license?') else 'free'
            license: dict[str, str] = {
                'key': key,
                'version': version
            }
            license_file.write(json.dumps(license, indent=2))

    def __yes_no_input(self, question: str) -> bool:
        while True:
            user_input = input(question + " [y/n]: ")
            try:
                return bool(strtobool(user_input))
            except ValueError:
                print("Please use y/n or yes/no.\n")