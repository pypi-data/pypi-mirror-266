from pathlib import Path
import argparse

from openverse_api_client._generate.python import generate_python
from openverse_api_client._generate.typescript import generate_typescript


arg_parser = argparse.ArgumentParser(
    prog="generate-openverse-api-client",
    description="Generate Openverse API clients for various languages.",
    epilog="If no language flags are passed, all languages will be generated. Otherwise, only the languages whose flags are passed will be generated.",
)

arg_parser.add_argument(
    "--ts",
    "--typescript",
    action=argparse.BooleanOptionalAction,
    dest="typescript",
    help="Control TypeScript client generation.",
)

arg_parser.add_argument(
    "--py",
    "--python",
    action=argparse.BooleanOptionalAction,
    dest="python",
    help="Control Python clients generation.",
)


def _python():
    python_files = generate_python()
    python_out = Path(__file__).parents[1]

    for file, source in python_files.items():
        path = python_out / file
        path.unlink(missing_ok=True)
        path.write_text(source)


def _typescript():
    typescript_files = generate_typescript()

    typescript_out = (
        Path(__file__).parents[3] / "packages" / "openverse-api-client" / "src"
    )

    for file, source in typescript_files.items():
        path = typescript_out / file
        path.unlink(missing_ok=True)
        path.write_text(source)


def generate(*, python=True, typescript=True):
    if python:
        _python()

    if typescript:
        _typescript()


def generate_cli():
    options = arg_parser.parse_args()

    if True in [options.python, options.typescript]:
        generate(
            python=options.python or False,
            typescript=options.typescript or False,
        )
    else:
        generate()
