import colorama
import deepl


class Error:
    __message: str

    def __init__(self, message: str = "Something went wrong!") -> None:
        self.__message = message
        print(f"\n\n{colorama.Fore.RED}{self.__message}\n")
        quit()


class HandlerError(Error):
    def __init__(self, message: str, source_file: str) -> None:
        self.__source_file = source_file
        message = f"Cannot read {self.__source_file}.\nMessage: {message}."
        super().__init__(message)


class DeeplError(Error):
    def __init__(self, exception: Exception) -> None:
        super().__init__(self.__get_message(exception))

    def __get_message(self, exception: Exception) -> str:
        if isinstance(exception, deepl.AuthorizationException):
            return "DeepL error: authorization failed, check your authentication key!"
        if isinstance(exception, deepl.QuotaExceededException):
            return "DeepL error: quota for this billing period has been exceeded!"
        if isinstance(exception, deepl.DocumentTranslationException):
            return f"Error translating document with id {exception.document_handle.id} and key {exception.document_handle.key}!"
        return "Error using DeepL API!"
