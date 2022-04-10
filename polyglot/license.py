import pathlib
from abc import ABC, abstractmethod


class LicenseManager(ABC):
    @abstractmethod
    def get_license(self) -> str:
        return ""

    @abstractmethod
    def set_license(self) -> None:
        pass


class CLILicenseManager(LicenseManager):
    def get_license(self) -> str:
        try:
            with open(self.__license_path, "r") as license_file:
                return license_file.read()
        except:
            return self.__set_and_get_license()

    def set_license(self) -> None:
        key: str = input("Type here your Deepl API key: ")
        with open(self.__license_path, "w+") as license_file:
            license_file.write(key.strip())

    @property
    def __license_path(self) -> str:
        return f"{pathlib.Path.home()}/.deepl_api_key.dat"

    def __set_and_get_license(self) -> str:
        self.set_license()
        return self.get_license()
