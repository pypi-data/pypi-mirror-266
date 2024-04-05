# -*- coding: utf-8 -*-
#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      24-11-2023
#
# Copyright 2023 Westcon-Comstor
#

# This is the Macal decompiler, it will decompile a .mbc file into bytecode mnenomics.

import argparse
import os
from typing import Optional

from macal.__about__ import __author__, __author_email__, __license__, __version__
from macal.config import SearchPath
from macal.macal_decompiler import MacalDecompiler

from macal.macal_binary_file_io import BINARY_FILE_EXTENSION, LoadBinary


def SetupSearchPath() -> None:
    search_path = [
        os.path.dirname(__file__),
        os.path.join(os.path.dirname(__file__), "lib"),
        os.path.join(os.path.dirname(__file__), "lib", "ext"),
        os.getcwd(),
        os.path.join(os.getcwd(), "lib"),
        os.path.join(os.getcwd(), "lib", "ext"),
    ]
    for path in search_path:
        if path not in SearchPath:
            SearchPath.append(path)


def check_file(file) -> Optional[str]:
    if file is None:
        raise ValueError("No file specified.")
    if not file.endswith(BINARY_FILE_EXTENSION):
        if os.path.exists(f"{file}{BINARY_FILE_EXTENSION}"):
            file = f"{file}{BINARY_FILE_EXTENSION}"
        else:
            raise Exception("Invalid Macal bytecode file.")
    return file


def BuildArgParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Macal decompiler")
    parser.add_argument("file", nargs="?", type=check_file, help="Macal file")
    parser.add_argument("-s", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("-v", "--version", action="version", version=f"Macal 2 interpreter v{__version__}")
    return parser


def Run():
    SetupSearchPath()
    parser = BuildArgParser()
    args = parser.parse_args()
    if args.file is None:
        parser.print_help()
        return
    if args.verbose:
        PrintBanner()
    code = LoadBinary(args.file)
    md = MacalDecompiler()
    md.Decompile(code)


def PrintBanner() -> None:
    print(f"Macal decompiler v{__version__}")
    print(f"Author:  {__author__}")
    print(f"Email:   {__author_email__}")
    print(f"License: {__license__}")
    print()


def PrintTokens(tokens: list) -> None:
    print("Tokens:")
    for token in tokens:
        print(token)
    print()


def PrintAst(ast) -> None:
    print("AST:")
    ast.tree()
    print()


if __name__ == "__main__":
    Run()
