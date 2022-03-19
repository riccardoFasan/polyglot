import colorama


class DeeplError(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(
            f"\n\n{colorama.Fore.RED}Status code: {status_code}.\nMessage: {message}\n"
        )
