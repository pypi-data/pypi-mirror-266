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

from typing import Any, List
import sys

from .macal_opcode import *
from .macal_binary_file_io import BINARY_FILE_EXTENSION, LoadBinary
from .ast_node_select_field import AstNodeSelectField



class MacalDecompiler:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def Decompile(self, code: list) -> None:
        for instruction in code:
            self._decompile_instruction(instruction, 0)

    def _get_opcode(self, opcode: int) -> str:
        if opcode in opcode_translation_table:
            return opcode_translation_table[opcode]
        else:
            return "UNKNOWN"

    def _decompile_instruction(self, instruction: list, indent: int) -> None:
        indent_str = " " * indent
        op = instruction[0]
        if op == Opcode_NEW_VARIABLE:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]}")
        elif op == Opcode_NEW_SCOPE:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]}")
        elif op == Opcode_LOAD_CONSTANT:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]}")
        elif op == Opcode_STORE_VARIABLE:
            var = self._decompile_expression(instruction[1][0])
            expr = self._decompile_expression(instruction[2][0])
            print(f"{indent_str}{opcode_translation_table[op]} {var} = {expr}")
        elif op == Opcode_LEAVE_SCOPE:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]}")
        elif op == Opcode_LOAD_LIBRARY:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]}")
        elif op == Opcode_PRINT:
            print(f"{indent_str}{opcode_translation_table[op]}({self._decompile_args(instruction[2])})")
        elif op == Opcode_EXTERN_FUNCTION_DEFINITION:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]} => ({self._decompile_expression(instruction[2])}) extern {instruction[3]}, {instruction[4]};")
        elif op == Opcode_IF or op == Opcode_ELIF:
            print(f"{indent_str}{opcode_translation_table[op]} {self._decompile_expression(instruction[1])}")
            print(f"{indent_str}{{ ")
            self._decompile_block(instruction[2], indent + 1)
            print(f"{indent_str}}} ")
        elif op == Opcode_CALL:
            print(f"{indent_str}{self._decompile_expression(instruction)}")
        elif op == Opcode_HALT:
            if len(instruction) == 1:
                print(f"{indent_str}{opcode_translation_table[op]}")
            else:
                print(f"{indent_str}{opcode_translation_table[op]} {self._decompile_expression(instruction[1])}")
        elif op == Opcode_RET:
            if len(instruction) == 1:
                print(f"{indent_str}{opcode_translation_table[op]}")
            else:
                print(f"{indent_str}{opcode_translation_table[op]} {self._decompile_expression(instruction[1])}")
        elif op == Opcode_CONTINUE:
            print(f"{indent_str}{opcode_translation_table[op]}")
        elif op == Opcode_BREAK:
            print(f"{indent_str}{opcode_translation_table[op]}")
        elif op == Opcode_FUNCTION_DEFINITION:
            print(f"{indent_str}{opcode_translation_table[op]} {instruction[1]} => ({instruction[2]})")
            print(f"{indent_str}{{ ")
            self._decompile_block(instruction[3], indent + 1)
            print(f"{indent_str}}} ")
        elif op == Opcode_SELECT:
            fields = self.parse_fields(instruction[1])
            from_table = self._decompile_expression(instruction[2]) + ' '
            where = self._decompile_expression(instruction[3])
            if len(where) > 0:
                where = ' where ' + where + ' '
            distinct = instruction[4]
            merge = instruction[5]
            into = 'into ' + self._decompile_expression(instruction[6])
            print(f"{indent_str}{opcode_translation_table[op]} select {'distinct ' if distinct else ''}{fields} from {from_table}{where}{'merge ' if merge else ''}{into}")
        elif op == Opcode_FOREACH:
            print(f"{indent_str}{opcode_translation_table[op]} {self._decompile_expression(instruction[1])}")
            print(f"{indent_str}{{ ")
            self._decompile_block(instruction[2], indent + 1)
            print(f"{indent_str}}} ")
        else:
            print(opcode_translation_table[op])
            print(f"we do not know this: {op} {instruction}")
            sys.exit(1)

    def parse_fields(self, fields: List[AstNodeSelectField]) -> str:
        result = ""
        for field in fields:
            if field.fieldname == field.altfieldname:
                result += field.fieldname + ', '
            else:
                result += field.fieldname + ' as ' + field.altfieldname + ', '
        return result[:-2]

    def _decompile_block(self, block: list, indent: int) -> None:
        for instruction in block:
            self._decompile_instruction(instruction, indent)

    def _decompile_args(self, args: list) -> str:
        result = ""
        if len(args) == 1:
            result = self._decompile_expression(args[0])
        elif len(args) > 1:
            for arg in args[:-1]:
                result += f"{self._decompile_expression(arg)}, "
            result += f"{self._decompile_expression(args[-1])}"
        return result
    
    def _decompile_expression_list(self, expr: list) -> str:
        result = ""
        if len(expr) == 1:
            result = self._decompile_expression(expr[0])
        elif len(expr) > 1:
            for e in expr[:-1]:
                result += f"{self._decompile_expression(e)}, "
            result += f"{self._decompile_expression(expr[-1])}"
        return result

    def _decompile_expression(self, expr) -> str:
        if isinstance(expr, list):
            return self._decompile_expression_list(expr)
        if len(expr) == 0:
            return ""
        op = expr[0]
        if op == Opcode_NEW_VARIABLE:
            return f"{opcode_translation_table[op]} {expr[1]}"
        elif op == Opcode_LOAD_CONSTANT:
            return f"{opcode_translation_table[op]} {expr[1]}"
        elif op == Opcode_LOAD_VARIABLE:
            index = ''
            if len(expr) > 2:
                index = f"[{self._decompile_expression(expr[2])}]"
            return f"{opcode_translation_table[op]} {expr[1]}{index} {expr}"
        elif op == Opcode_ADD :
            lhs = self._decompile_expression(expr[1])
            rhs = self._decompile_expression(expr[2])
            return f"{lhs} + {rhs}"
        elif op == Opcode_SUB :
            lhs = self._decompile_expression(expr[1])
            rhs = self._decompile_expression(expr[2])
            return f"{lhs} - {rhs}"
        elif op == Opcode_MUL :
            lhs = self._decompile_expression(expr[1])
            rhs = self._decompile_expression(expr[2])
            return f"{lhs} * {rhs}"
        elif op == Opcode_DIV :
            lhs = self._decompile_expression(expr[1])
            rhs = self._decompile_expression(expr[2])
            return f"{lhs} / {rhs}"
        elif op == Opcode_MOD :
            lhs = self._decompile_expression(expr[1])
            rhs = self._decompile_expression(expr[2])
            return f"{lhs} % {rhs}"
        elif op == Opcode_POW :
            lhs = self._decompile_expression(expr[1])
            rhs = self._decompile_expression(expr[2])
            return f"{lhs} ** {rhs}"
        elif op == Opcode_GTE :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} >= {rhs}"
        elif op == Opcode_LTE :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} <= {rhs}"
        elif op == Opcode_EQ  :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} == {rhs}"
        elif op == Opcode_NEQ :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} != {rhs}"
        elif op == Opcode_GT :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} > {rhs}"
        elif op == Opcode_LT :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} < {rhs}"
        elif op == Opcode_AND :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} and {rhs}"
        elif op == Opcode_OR :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} or {rhs}"
        elif op == Opcode_XOR :
            lhs = self._decompile_expression(expr[1][0])
            rhs = self._decompile_expression(expr[2][0])
            return f"{lhs} xor {rhs}"
        elif op == Opcode_CALL:
            return f"{opcode_translation_table[op]} {expr[1]}({self._decompile_args(expr[3])})"
        else:
            raise Exception(f"Unknown expression {expr}")


