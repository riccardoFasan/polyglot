from abc import ABC, abstractmethod

from polyglot import commands, license
from polyglot.utils import DownloadedDocumentStream


class EngineConnector(ABC):

    _license: str
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
    ) -> DownloadedDocumentStream:
        pass


class DeeplConnector(EngineConnector):
    def print_usage_info(self) -> None:
        return commands.PrintUsageInfo(self._license).execute()

    def print_supported_languages(self) -> None:
        return commands.PrintSupportedLanguages(self._license).execute()

    def translate(self, content: str, target_lang: str, source_lang: str = "") -> str:
        return commands.TranslateText(
            self._license, content, target_lang, source_lang
        ).execute()

    def translate_document(
        self, source_file: str, target_lang: str, source_lang: str = ""
    ) -> DownloadedDocumentStream:
        return commands.TranslateDocumentCommand(
            self._license, source_file, target_lang, source_lang
        ).execute()
