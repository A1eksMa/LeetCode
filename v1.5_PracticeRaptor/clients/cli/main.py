#!/usr/bin/env python3
"""
PracticeRaptor CLI - Practice coding problems with rapid feedback.

Usage:
    python -m clients.cli.main [--task N] [--file solution.py] [--verbose]

Options:
    --task N        Jump to problem #N
    --file FILE     Load solution from file
    --verbose       Verbose output
    --config PATH   Path to config file
    --help          Show this help
"""
import argparse
import sys
from pathlib import Path

from di import load_config, create_container
from .app import CLIApp


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PracticeRaptor CLI - Practice coding problems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m clients.cli.main                    Interactive mode
  python -m clients.cli.main --task 2           Jump to problem #2
  python -m clients.cli.main --task 1 --file solution.py
  python -m clients.cli.main --verbose          Verbose output
        """,
    )

    parser.add_argument(
        "--task",
        "-t",
        type=int,
        help="Problem number",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="Solution file path",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("config/config.yaml"),
        help="Config file path",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return 1

    # Create DI container
    try:
        container = create_container(config)
    except Exception as e:
        print(f"Error initializing application: {e}", file=sys.stderr)
        return 1

    # Create and run app
    app = CLIApp(container)

    try:
        return app.run(
            task_id=args.task,
            file_path=args.file,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # For multiprocessing on all platforms
    import multiprocessing as mp

    mp.set_start_method("spawn", force=True)

    sys.exit(main())
