#!/usr/bin/env python3

from polyglot import arguments
from polyglot import translator


def main() -> None:
    try:
        collector: arguments.ArgumentsCollector = arguments.CLIArgumentsCollector()
        args: arguments.Arguments = collector.arguments
        translator.Translator(args).execute_command()
    except KeyboardInterrupt:
        print('\n\nInterrupted by user.')


if __name__ == '__main__':
    main()
