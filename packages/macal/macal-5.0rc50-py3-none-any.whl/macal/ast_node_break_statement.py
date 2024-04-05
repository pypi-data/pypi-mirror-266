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

# This is the AST node for a break statement.

from __future__ import annotations

from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken

class AstNodeBreakStatement(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeBreakStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.BREAK_STATEMENT

    def __str__(self) -> str:
        return f"BreakStatement()"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}BreakStatement()")
