import colorama


class DeeplError(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        if status_code == 403:
            message = f"{message}.\nCheck that your licence is valid"
        super().__init__(
            f"\n\n{colorama.Fore.RED}Status code: {status_code}.\nMessage: {message}.\n"
        )


class HandlerError(Exception):
    source_file: str
    message: str

    def __init__(self, source_file: str, message: str):
        self.source_file = source_file
        self.message = message
        super().__init__(
            f"\n\n{colorama.Fore.RED}Cannot read {self.source_file}.\nMessage: {message}.\n"
        )
