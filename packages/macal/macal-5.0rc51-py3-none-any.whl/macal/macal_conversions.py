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

# This module contains the conversion utilities for the Macal language.

from typing import Any

from .ast_nodetype import AstNodetype
from .lex_token import LexToken


def convertToHex(value: int, digits: int = 4, prefix: str = "") -> str:
    if isinstance(value, int):
        return f"{prefix}{value:0{digits}X}"
    return f"{value}".strip()


def convertToValue(token: LexToken) -> Any:
    if token.token_type == AstNodetype.INTEGER:
        return int(token.value)
    elif token.token_type == AstNodetype.FLOAT:
        return float(token.value)
    elif (
        token.token_type == AstNodetype.STRING
        or token.token_type == AstNodetype.STRING_INTERPOLATION_STRING_PART
        or token.token_type == AstNodetype.STRING_INTERPOLATION_END
    ):
        # return token.value
        return token.value[1:-1]
    elif token.token_type == AstNodetype.BOOLEAN:
        return token.value == "true"
    elif token.token_type == AstNodetype.BOOLEAN_TRUE:
        return True
    elif token.token_type == AstNodetype.BOOLEAN_FALSE:
        return False
    elif token.token_type == AstNodetype.NIL:
        return None
    else:
        raise Exception(f"convertToValue(): Unknown type {token.token_type}")


def compareTypes(type1: AstNodetype, type2: AstNodetype) -> bool:
    if type1 == type2:
        return True
    # handle the oddball cases
    if type1 == AstNodetype.STRING_INTERPOLATION_STRING_PART or type1 == AstNodetype.STRING_INTERPOLATION_END:
        type1 = AstNodetype.STRING
    if type2 == AstNodetype.STRING_INTERPOLATION_STRING_PART or type2 == AstNodetype.STRING_INTERPOLATION_END:
        type2 = AstNodetype.STRING
    return type1 == type2


def typeFromValue(value: Any) -> AstNodetype:
    # BOOLEAN BEFORE INTEGER as BOOLEAN is a subclass of INTEGER
    if isinstance(value, bool):
        return AstNodetype.BOOLEAN
    elif isinstance(value, int):
        return AstNodetype.INTEGER
    elif isinstance(value, float):
        return AstNodetype.FLOAT
    elif isinstance(value, str):
        return AstNodetype.STRING
    elif value is None or value == "nil" or value == AstNodetype.NIL:
        return AstNodetype.NIL
    elif isinstance(value, list):
        return AstNodetype.ARRAY
    elif isinstance(value, dict):
        return AstNodetype.RECORD
    else:
        raise Exception(f"typeFromValue(): Unknown type {type(value)}")


def convertToHexAddr(addr: int) -> str:
    return f"0x{addr:08X}"

def typeToStr(value_type: AstNodetype) -> str:
    if value_type == AstNodetype.BOOLEAN:
        return "boolean"
    elif value_type == AstNodetype.INTEGER:
        return "integer"
    elif value_type == AstNodetype.FLOAT:
        return "float"
    elif value_type == AstNodetype.STRING:
        return "string"
    elif value_type == AstNodetype.ARRAY:
        return "array"
    elif value_type == AstNodetype.RECORD:
        return "record"
    elif value_type == AstNodetype.NIL:
        return "nil"
    elif value_type == AstNodetype.FUNCTION:
        return "function"
    elif value_type == AstNodetype.PARAMS:
        return "params"
    elif value_type == AstNodetype.VARIABLE:
        return "variable"
    else:
        return "unknown type"
    
    
def pythonTypeToStr(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "string"
    elif value is None or value == "nil" or value == AstNodetype.NIL:
        return "nil"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "record"
    else:
        return type(value).__name__