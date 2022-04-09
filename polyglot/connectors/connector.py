from abc import ABC, abstractmethod

from polyglot import license


class EngineConnector(ABC):

    _license: license.License
    __license_manager: license.LicenseManager

    def __init__(
        self,
        license_manager: license.LicenseManager,
    ) -> None:
        self.__license_manager = license_manager
        self._license = self.__license_manager.get_license()

    @abstractmethod
    def print_usage_info(self) -> None:
        pass

    @abstractmethod
    def print_supported_languages(self) -> None:
        pass

    @abstractmethod
    def translate(self, content: str, target_lang: str, source_lang: str = "") -> str:
        pass

    @abstractmethod
    def translate_document(
        self, source_file: str, target_lang: str, source_lang: str = ""
    ) -> bytes:
        pass
