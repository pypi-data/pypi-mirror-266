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

# This dictionary table maps the statement type to the corresponding statement lexeme.

from .ast_nodetype import AstNodetype

StatementTypeTable = {
    "const": AstNodetype.CONST_STATEMENT,
    "if": AstNodetype.IF_STATEMENT,
    "else": AstNodetype.ELSE_STATEMENT,
    "elif": AstNodetype.ELIF_STATEMENT,
    "foreach": AstNodetype.FOREACH_STATEMENT,
    "while": AstNodetype.WHILE_STATEMENT,
    "continue": AstNodetype.CONTINUE_STATEMENT,
    "break": AstNodetype.BREAK_STATEMENT,
    "return": AstNodetype.RETURN_STATEMENT,
    "select": AstNodetype.SELECT_STATEMENT,
    "distinct": AstNodetype.DISTINCT_STATEMENT,
    "as": AstNodetype.AS_STATEMENT,
    "from": AstNodetype.FROM_STATEMENT,
    "where": AstNodetype.WHERE_STATEMENT,
    "order": AstNodetype.ORDER_STATEMENT,
    "merge": AstNodetype.MERGE_STATEMENT,
    "into": AstNodetype.INTO_STATEMENT,
    "halt": AstNodetype.HALT_STATEMENT,
    "include": AstNodetype.INCLUDE_STATEMENT,
    "external": AstNodetype.EXTERNAL_STATEMENT,
    "print": AstNodetype.PRINT_STATEMENT,
    "switch": AstNodetype.SWITCH_STATEMENT,
    "case": AstNodetype.CASE_STATEMENT,
    "default": AstNodetype.DEFAULT_STATEMENT,
    "false": AstNodetype.BOOLEAN,
    "true": AstNodetype.BOOLEAN,
    "nil": AstNodetype.NIL,
    "and": AstNodetype.AND_STATEMENT,
    "or": AstNodetype.OR_STATEMENT,
    "not": AstNodetype.NOT_STATEMENT,
    "xor": AstNodetype.XOR_STATEMENT,
    "integer": AstNodetype.INTEGER,
    "float": AstNodetype.FLOAT,
    "string": AstNodetype.STRING,
    "variable": AstNodetype.VARIABLE,
    "function": AstNodetype.FUNCTION,
    "bool": AstNodetype.BOOLEAN,
    "array": AstNodetype.ARRAY,
    "record": AstNodetype.RECORD,
    "params": AstNodetype.PARAMS,
    "Type": AstNodetype.TYPE_STATEMENT,
    "IsString": AstNodetype.IS_STRING_STATEMENT,
    "IsInt": AstNodetype.IS_INT_STATEMENT,
    "IsFloat": AstNodetype.IS_FLOAT_STATEMENT,
    "IsBool": AstNodetype.IS_BOOL_STATEMENT,
    "IsRecord": AstNodetype.IS_RECORD_STATEMENT,
    "IsArray": AstNodetype.IS_ARRAY_STATEMENT,
    "IsFunction": AstNodetype.IS_FUNCTION_STATEMENT,
    "IsNil": AstNodetype.IS_NIL_STATEMENT,
}
