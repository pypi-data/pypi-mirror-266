# -*- coding: utf-8 -*-
#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      2023-11-23
#
# Copyright 2023 Westcon-Comstor
#

# This is the new Macal Compiler, it will lex, parse, compile the source file and saves the result into a binary file.

import argparse
import os
import sys

from .__about__ import __author__, __author_email__, __license__, __version__
from .config import SearchPath
from .macal_compiler import MacalCompiler
from .macal_lexer import Lexer
from .macal_parser import Parser
from .macal_binary_file_io import (
    BINARY_FILE_EXTENSION,
    SOURCE_FILE_EXTENSION,
    SaveBinary,
)


def SetupSearchPath():
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


def check_file(file) -> str:
    if file is None:
        raise ValueError("No Macal source file provided.")
    if not file.endswith(BINARY_FILE_EXTENSION) and not file.endswith(
        SOURCE_FILE_EXTENSION
    ):
        if os.path.exists(f"{file}{SOURCE_FILE_EXTENSION}"):
            file = f"{file}{SOURCE_FILE_EXTENSION}"
        else:
            raise Exception("Invalid Macal source file.")
    return file


def BuildArgParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Macal compiler")
    parser.add_argument("file", nargs="?", type=check_file, help="Macal file")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument(
        "-r",
        "--reserved",
        help="a csv list of reserved variables",
        default="",
        required=False,
        type=str,
    )
    parser.add_argument("-s", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument(
        "-v", "--version", action="version", version=f"Macal 2 compiler v{__version__}"
    )
    return parser


def LoadSource(fileName) -> str:
    with open(fileName, "r") as f:
        text = f.read()
    return str(text)


def FromSource(args, file: str, output_filename: str) -> None:
    try:
        # Lex
        source = LoadSource(file)
        tokens = Lexer(source).tokenize()
        if args.verbose:
            PrintTokens(tokens)

        # Parse
        ast = Parser(tokens, args.file).parse()
        if args.verbose:
            PrintAst(ast)

        # Handle reserved variables from the CLI
        reserved = []
        if args.reserved != "":
            reserved = args.reserved.split(",")

        # compile
        compiler = MacalCompiler(verbose=args.verbose)
        instructions = compiler.Compile(ast, reserved)

        # save binary file
        SaveBinary(output_filename, instructions)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def Run():
    SetupSearchPath()
    parser = BuildArgParser()
    args = parser.parse_args()
    if args.file is None:
        parser.print_help()
        return
    output_filename = str(
        args.output or args.file.replace(SOURCE_FILE_EXTENSION, BINARY_FILE_EXTENSION)
    )
    if args.verbose:
        PrintBanner()
    print(f"Compiling {args.file} to {output_filename}")
    FromSource(args, args.file, output_filename)
    print(f"Compiled to {output_filename}")


def PrintBanner() -> None:
    print(f"Macal compiler v{__version__}")
    print(f"Author:  {__author__}")
    print(f"Email:   {__author_email__}")
    print(f"License: {__license__}")


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
