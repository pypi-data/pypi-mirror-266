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

# This is the node object for an array literal expression.

from __future__ import annotations

from .ast_node_literal_expression import AstNodeLiteralExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeLiteralArrayExpression(AstNodeLiteralExpression):
    def __init__(self, token: LexToken, array: list) -> AstNodeLiteralArrayExpression:
        super().__init__(token)
        self.expr_type = AstNodetype.LITERAL_ARRAY_EXPRESSION
        self.array: list = array

    def tree(self, indent: str = "") -> None:
        print(f"{indent}LiteralArrayExpression:")
        print(f"    {indent}", end="")
        for item in self.array:
            print(item, end=", ")
        print()

    def value(self) -> list:
        return self.array

    def __str__(self) -> str:
        return f"AstNodeLiteralArrayExpression({self.token})"

    def __repr__(self) -> str:
        return self.__str__()
