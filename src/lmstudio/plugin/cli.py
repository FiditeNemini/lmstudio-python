"""Command line interface implementation."""

import argparse
import logging
import os.path
import sys
import warnings

from typing import Sequence

from ..sdk_api import sdk_public_api

from . import _dev_runner, runner


def _parse_args(
    argv: Sequence[str] | None = None,
) -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    py_name = os.path.basename(sys.executable).removesuffix(".exe")
    parser = argparse.ArgumentParser(
        prog=f"{py_name} -m {__spec__.parent}",
        description="LM Studio plugin runner for Python plugins",
    )
    parser.add_argument(
        "plugin_path", metavar="PLUGIN_PATH", help="Directory name of plugin to run"
    )
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser, parser.parse_args(argv)


@sdk_public_api()
def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``lmstudio.plugin`` CLI.

    If *args* is not given, defaults to using ``sys.argv``.
    """
    parser, args = _parse_args(argv)
    plugin_path = args.plugin_path
    if not os.path.exists(plugin_path):
        parser.print_usage()
        print(f"ERROR: Failed to find plugin folder at {plugin_path!r}")
        return 1
    warnings.filterwarnings(
        "ignore", ".*the plugin API is not yet stable", FutureWarning
    )
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    if not args.dev:
        try:
            runner.run_plugin(plugin_path, allow_local_imports=True)
        except KeyboardInterrupt:
            print("Plugin execution terminated with Ctrl-C")
    else:
        # Retrieve args from API host, spawn plugin in subprocess
        try:
            _dev_runner.run_plugin(plugin_path, debug=args.debug)
        except KeyboardInterrupt:
            pass  # Subprocess handles reporting the plugin termination
    return 0
