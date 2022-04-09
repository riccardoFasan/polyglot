import requests
import urllib.parse
from requests import Response

from polyglot import license


class DeeplClient:

    _license: str
    __DEEPL_API_URL = "https://api.deepl.com/v2"
    __DEEPL_API_URL_FREE = "https://api-free.deepl.com/v2"

    def __init__(self, license: str) -> None:
        self._license = license

    @property
    def __base_url(self) -> str:
        return (
            self.__DEEPL_API_URL_FREE
            if self._license.endswith(":fx")
            else self.__DEEPL_API_URL
        )

    @property
    def __headers(self) -> dict[str, str]:
        return {
            "Authorization": f"DeepL-Auth-Key {self._license}",
            "Content-Type": "application/json",
        }

    def get_usage_info(self) -> Response:
        return requests.get(f"{self.__base_url}/usage", headers=self.__headers)

    def get_supported_languages(self) -> Response:
        return requests.get(
            f"{self.__base_url}/languages",
            headers=self.__headers,
        )

    def translate(self, entry: str, target_lang: str, source_lang: str) -> Response:
        escaped_entry: str = urllib.parse.quote(entry)
        endpoint: str = f"{self.__base_url}/translate?auth_key={self._license}&text={escaped_entry}&target_lang={target_lang}"

        if source_lang != "":
            endpoint += f"&source_lang={source_lang}"

        return requests.get(endpoint)

    def upload_document(
        self, file: str, target_lang: str, source_lang: str
    ) -> Response:
        request_data: dict[str, str] = {
            "target_lang": target_lang,
            "auth_key": self._license,
            "filename": file,
        }

        if source_lang != "":
            request_data["source_lang"] = source_lang

        endpoint: str = f"{self.__base_url}/document/"

        with open(file, "rb") as document:
            return requests.post(endpoint, data=request_data, files={"file": document})

    def get_document_status(self, document_id: str, document_key: str) -> Response:
        endpoint: str = f"{self.__base_url}/document/{document_id}?auth_key={self._license}&document_key={document_key}"
        return requests.post(endpoint)

    def download_document(self, document_id: str, document_key: str) -> Response:
        endpoint: str = f"{self.__base_url}/document/{document_id}/result?auth_key={self._license}&document_key={document_key}"
        return requests.post(endpoint)
