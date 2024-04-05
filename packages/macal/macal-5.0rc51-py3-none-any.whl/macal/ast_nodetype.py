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


# Node type definitions for Macal

from enum import Enum, auto


class AstNodetype(Enum):
    UNDEFINED = 127

    # types used at runtime
    INTEGER = auto()  # 128
    FLOAT = auto()  # 129
    STRING = auto()  # 130
    BOOLEAN = auto()  # 131
    ARRAY = auto()  # 132
    RECORD = auto()  # 133
    VARIABLE = auto()  # 134
    FUNCTION = auto()  # 135
    TYPE = auto()  # 136
    NIL = auto()  # 137
    LIBRARY = auto()  # 138
    LABEL = auto()  # 139
    BC_METADATA = auto()  # 130
    STRING_INTERPOLATION_STRING_PART = auto()  # 131
    STRING_INTERPOLATION_END = auto()  # 132

    REGISTER = auto()  # 133

    VM_INSTRUCTION = auto()
    # Token types
    IDENTIFIER = auto()
    WHITESPACE = auto()
    COMMENT = auto()
    EOF = auto()
    # variable types
    BOOLEAN_TRUE = auto()
    BOOLEAN_FALSE = auto()
    STRING_INTERPOLATION_START = auto()
    NEW_RECORD = auto()
    NEW_ARRAY = auto()
    INDEX = auto()
    ANY = auto()
    PARAMS = auto()
    # Operator type LexTokens
    OPERATOR_ARROW = auto()
    OPERATOR_ADDITION = auto()
    OPERATOR_SUBTRACTION = auto()
    OPERATOR_MULTIPLICATION = auto()
    OPERATOR_DIVISION = auto()
    OPERATOR_POWER = auto()
    OPERATOR_MODULUS = auto()
    OPERATOR_ASSIGNMENT = auto()
    OPERATOR_INCREMENT = auto()
    OPERATOR_DECREMENT = auto()
    OPERATOR_ASSIGNMENT_INC = auto()
    OPERATOR_ASSIGNMENT_DEC = auto()
    OPERATOR_ASSIGNMENT_MUL = auto()
    OPERATOR_ASSIGNMENT_DIV = auto()
    OPERATOR_ASSIGNMENT_MOD = auto()
    OPERATOR_ASSIGNMENT_POW = auto()
    OPERATOR_ASSIGNMENT_NEG = auto()
    # Comparison type LexTokens
    COMPARETOR_EQUAL = auto()
    COMPARETOR_NOT_EQUAL = auto()
    COMPARETOR_LESS_THAN = auto()
    COMPARETOR_LESS_THAN_EQUAL = auto()
    COMPARETOR_GREATER_THAN = auto()
    COMPARETOR_GREATER_THAN_EQUAL = auto()
    AND_STATEMENT = auto()
    OR_STATEMENT = auto()
    NOT_STATEMENT = auto()
    XOR_STATEMENT = auto()
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_NOT = auto()
    # Punctuation LexTokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()  # not implemented
    DOT = auto()  # not implemented
    # AST Node types
    PROGRAM = auto()
    BLOCK = auto()
    END_BLOCK = auto()
    FUNCTION_CALL = auto()
    FUNCTION_DEFINITION = auto()

    IF_STATEMENT = auto()
    ELIF_STATEMENT_LIST = auto()
    ELIF_STATEMENT = auto()
    ELSE_STATEMENT = auto()
    FOREACH_STATEMENT = auto()
    WHILE_STATEMENT = auto()
    CONTINUE_STATEMENT = auto()
    BREAK_STATEMENT = auto()
    RETURN_STATEMENT = auto()
    SELECT_STATEMENT = auto()
    SELECT_FIELD = auto()
    DISTINCT_STATEMENT = auto()
    AS_STATEMENT = auto()
    FROM_STATEMENT = auto()
    WHERE_STATEMENT = auto()
    ORDER_STATEMENT = auto()
    MERGE_STATEMENT = auto()
    INTO_STATEMENT = auto()
    HALT_STATEMENT = auto()
    INCLUDE_STATEMENT = auto()
    EXTERNAL_STATEMENT = auto()
    PRINT_STATEMENT = auto()
    CONST_STATEMENT = auto()
    SWITCH_STATEMENT = auto()
    CASE_STATEMENT = auto()
    DEFAULT_STATEMENT = auto()
    ASSIGNMENT_STATEMENT = auto()
    TYPE_STATEMENT = auto()
    IS_STRING_STATEMENT = auto()
    IS_INT_STATEMENT = auto()
    IS_FLOAT_STATEMENT = auto()
    IS_BOOL_STATEMENT = auto()
    IS_RECORD_STATEMENT = auto()
    IS_ARRAY_STATEMENT = auto()
    IS_FUNCTION_STATEMENT = auto()
    IS_NIL_STATEMENT = auto()
    IS_TYPE_STATEMENT = auto()
    
    # expressions
    EXPRESSION = auto()
    INDEXED_VARIABLE_EXPRESSION = auto()
    VARIABLE_EXPRESSION = auto()
    FUNCTION_CALL_EXPRESSION = auto()
    VARIABLE_FUNCTION_CALL_EXPRESSION = auto()
    LIBRARY_EXPRESSION = auto()
    LITERAL_EXPRESSION = auto()
    LITERAL_ARRAY_EXPRESSION = auto()
    LITERAL_RECORD_EXPRESSION = auto()
    UNARY_EXPRESSION = auto()
    BINARY_EXPRESSION = auto()
    TERNARY_EXPRESSION = auto()  # not implemented
    REGISTER_EXPRESSION = auto()
    
    # misc 2
    BC_VERSION = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


if max([e.value for e in AstNodetype]) > 512:
    raise Exception("Too many AstNodetypes.  Max is 512.")
