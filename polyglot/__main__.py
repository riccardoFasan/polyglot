#!/usr/bin/env python3

from colorama import init

from polyglot.arguments import Arguments, ArgumentsCollector, CLIArgumentsCollector
from polyglot.translator import execute_command


init(autoreset=True)


def translate_or_print_data() -> None:
    collector: ArgumentsCollector = CLIArgumentsCollector()
    args: Arguments = collector.arguments
    execute_command(args)


if __name__ == '__main__':
    try:
        translate_or_print_data()
    except KeyboardInterrupt:
        print('\n\nInterrupted by user.')
