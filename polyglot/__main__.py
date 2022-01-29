#!/usr/bin/env python3

from polyglot import arguments
from polyglot import translator


def translate_or_print_data() -> None:
    collector: arguments.ArgumentsCollector = arguments.CLIArgumentsCollector()
    args: arguments.Arguments = collector.arguments
    translator.execute_command(args)


if __name__ == '__main__':
    try:
        translate_or_print_data()
    except KeyboardInterrupt:
        print('\n\nInterrupted by user.')
