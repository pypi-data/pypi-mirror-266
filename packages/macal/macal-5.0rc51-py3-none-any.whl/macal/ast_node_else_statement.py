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

# This is the else statement AST node.

from __future__ import annotations

from .ast_node_block import AstNodeBlock
from .ast_nodetype import AstNodetype
from .lex_token import LexToken

class AstNodeElseStatement(AstNodeBlock):
    def __init__(self, token: LexToken) -> AstNodeElseStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.ELSE_STATEMENT

    def __str__(self) -> str:
        return f"AstNodeElseStatement({self.statements})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}ElseStatement:")
        super().tree(indent + "    ")
