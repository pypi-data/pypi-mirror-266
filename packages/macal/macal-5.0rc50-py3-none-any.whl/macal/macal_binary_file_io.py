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

# These functions provide a way to save and load Macal compiled "bytecode".

from typing import Any
import pickle

MAGIC_BYTES: bytes = b'BMC'
FILE_FORMAT_VERSION: int = 5
BINARY_FILE_EXTENSION: str = '.mcb'
SOURCE_FILE_EXTENSION: str = '.mcl'

def SaveBinary(filename: str, data: Any) -> None:
    if not filename.endswith(BINARY_FILE_EXTENSION):
        filename += BINARY_FILE_EXTENSION
    with open(filename, 'wb') as f:
        f.write(MAGIC_BYTES)
        f.write(FILE_FORMAT_VERSION.to_bytes(4, byteorder='little'))
        code = pickle.dumps(data)
        code_size = len(code)
        f.write(code_size.to_bytes(4, byteorder='little'))
        f.write(code)

def LoadBinary(filename: str) -> Any:
    if not filename.endswith(BINARY_FILE_EXTENSION):
        filename += BINARY_FILE_EXTENSION
    with open(filename, 'rb') as f:
        magic = f.read(3)
        if magic != MAGIC_BYTES:
            raise Exception(f'Invalid magic bytes: {magic}')
        version = int.from_bytes(f.read(4), byteorder='little')
        if version != FILE_FORMAT_VERSION:
            raise Exception(f'Invalid file format version: {version}')
        code_size = int.from_bytes(f.read(4), byteorder='little')
        code = f.read(code_size)
        return pickle.loads(code)
