from distutils.util import strtobool
import colorama


def get_truncated_text(text: str, limit: int) -> str:
    return text[:limit] + "..." if len(text) > limit else text


def get_color_by_percentage(percentage: int) -> str:
    if percentage > 90:
        return colorama.Fore.RED
    if percentage > 60:
        return colorama.Fore.YELLOW
    return colorama.Fore.RESET


def yes_no_input(question: str) -> bool:
    while True:
        user_input = input(question + " [y/n]: ")
        try:
            return bool(strtobool(user_input))
        except ValueError:
            print("Please use y/n or yes/no.\n")
