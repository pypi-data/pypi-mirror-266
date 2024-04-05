# -*- coding: utf-8 -*-
#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      23-11-2023
#
# Copyright 2023 Westcon-Comstor
#

# This is the new Macal Runtime, it interpret/execute a compiled Macal (.mcb) file.

import argparse
import os

from .__about__ import __author__, __author_email__, __license__, __version__
from .config import SearchPath

import pyximport; pyximport.install()
from .macal_vm import MacalVm
from .macal_binary_file_io import BINARY_FILE_EXTENSION, LoadBinary



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
    if not file.endswith(BINARY_FILE_EXTENSION):
        if os.path.exists(f"{file}{BINARY_FILE_EXTENSION}"):
            file = f"{file}{BINARY_FILE_EXTENSION}"
        else:
            raise Exception("Invalid Macal bytecode file.")
    return file


def BuildArgParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Macal runtime")
    parser.add_argument("file", nargs="?", type=check_file, help=f"Macal bytecode file ({BINARY_FILE_EXTENSION})")
    parser.add_argument("-v", "--version", action="version", version=f"Macal runtime v{__version__}")
    return parser


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
    if args.file is None:
        parser.print_help()
        return
    code = LoadBinary(args.file)
    vm = MacalVm(verbose=False)
    vm.Execute(code)
    ShowResult(vm.exitcode)


if __name__ == "__main__":
    Run()
