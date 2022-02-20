#!/usr/bin/env python3

from polyglot import arguments, polyglot


def main() -> None:
    try:
        collector: arguments.ArgumentsCollector = arguments.CLIArgumentsCollector()
        options: arguments.Arguments = collector.arguments
        polyglot.Polyglot(options).execute_command()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")


if __name__ == "__main__":
    main()
