# -*- coding: utf-8 -*-
#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      24-10-2023
#
# Copyright 2023 Westcon-Comstor
#

# This is the Macal Interpreter, it will lex, parse, compile and interpret (execute).

import argparse
import os

from .__about__ import __author__, __author_email__, __license__, __version__
from .config import SearchPath

from .macal_lexer import Lexer
from .macal_parser import Parser
from .macal_compiler import MacalCompiler

from .macal_binary_file_io import BINARY_FILE_EXTENSION, SOURCE_FILE_EXTENSION, LoadBinary, SaveBinary

import pyximport; pyximport.install()
from .macal_vm import MacalVm


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
        raise ValueError("No file specified.")
    if not file.endswith(BINARY_FILE_EXTENSION) and not file.endswith(SOURCE_FILE_EXTENSION):
        if os.path.exists(f"{file}{SOURCE_FILE_EXTENSION}"):
            file = f"{file}{SOURCE_FILE_EXTENSION}"
        else:
            raise Exception("Invalid Macal source file.")
    return file


def BuildArgParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Macal interpreter")
    parser.add_argument("file", nargs="?", type=check_file, help="Macal file")
    parser.add_argument("-d", "--decompile", action="store_true", help="Execute decompiler")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("-n", "--noexec", action="store_true", help="Do not execute")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-p", "--profile", action="store_true", help="Profile mode")
    parser.add_argument("-r", "--reserved", help="a csv list of reserved variables", default="", required=False, type=str)
    parser.add_argument("-s", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("-v", "--version", action="version", version=f"Macal 2 interpreter v{__version__}")
    return parser


def LoadSource(fileName) -> str:
    with open(fileName, "r") as f:
        text = f.read()
    return str(text)

def Execute(filename: str, profile: bool = False) -> int:
    code = LoadBinary(filename)
    vm = MacalVm(verbose=False)
    if profile:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            vm.Execute(code)
        result = pstats.Stats(pr)
        result.sort_stats("cumulative")
        result.print_stats()
    else:
        vm.Execute(code)
        pass
    return vm.exitcode

def FromExecutable(args, file: str) -> None:
    #if args.decompile:
    #    MacalDecompiler(file).Decompile()
    if not args.noexec:
        ShowResult(Execute(file, args.profile))
    pass

def FromSource(args, file: str, output_filename: str, no_output: bool) -> None:
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
    if not no_output:
        SaveBinary(output_filename, instructions)

    if not args.noexec:
        # execute (interpret)
        vm = MacalVm(verbose=args.verbose)
        vm.Execute(instructions)
        ShowResult(vm.exitcode)
    else:
        print("No execution requested.")

def ShowResult(exitCode: int) -> None:
    if exitCode == 0:
        print("Process exits OK")
    else:
        print(f"Process exits with error: {exitCode}")
    exit(exitCode)


def Run():
    SetupSearchPath()
    parser = BuildArgParser()
    args = parser.parse_args()
    if args.interactive:
        print("Interactive mode is not available yet.")
        return
        from macal.macal_interactive import MacalInteractive

        MacalInteractive().Run()
        return
    if args.file is None:
        parser.print_help()
        return
    output_filename = str(args.output or args.file.replace(SOURCE_FILE_EXTENSION, BINARY_FILE_EXTENSION))
    no_output = False
    if args.output is None:
        no_output = True
    if args.file.endswith(BINARY_FILE_EXTENSION):
        FromExecutable(args, args.file)
        return
    FromSource(args, args.file, output_filename, no_output)


def PrintBanner() -> None:
    print(f"Macal interpreter v{__version__}")
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
