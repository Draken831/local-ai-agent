from __future__ import annotations

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="MSP AI Agent launcher")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Start the command-line interface instead of the default GUI.",
    )
    args = parser.parse_args()

    if args.cli:
        from .cli import main as cli_main
        return cli_main()

    try:
        from .gui import main as gui_main
        return gui_main()
    except Exception as exc:
        # Do not silently fall back to CLI; the requested default interface is GUI.
        print(f"GUI failed to start: {exc}", file=sys.stderr)
        print("For diagnostic CLI mode run: msp-agent --cli", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
