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

# This is the root, program node for the AST.

from __future__ import annotations

from .ast_node_block import AstNodeBlock
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeProgram(AstNodeBlock):
    def __init__(self, filename: str) -> AstNodeProgram:
        super().__init__(LexToken(type=AstNodetype.PROGRAM, lineno=1, offset=1, lexpos=0, value=filename, filename=filename))
        self.expr_type = AstNodetype.PROGRAM
        self.filename: str = filename

    def __str__(self) -> str:
        return f"AstNodeProgram({self.statements})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self) -> None:
        print(f"Program: {self.filename}")
        for statement in self.statements:
            statement.tree("    ")
