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

# This is a unary expression AST node.

from __future__ import annotations

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeUnaryExpression(AstNodeExpression):
    def __init__(self, token: LexToken, right: AstNodeExpression) -> AstNodeUnaryExpression:
        super().__init__(token)
        self.expr_type = AstNodetype.UNARY_EXPRESSION
        self.right: AstNodeExpression = right
        self.op: LexToken = token

    def __str__(self) -> str:
        return f"AstNodeUnaryExpression({self.token.value}, {self.right})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}UnaryExpression:")
        print(
            f"{indent}    {self.token.value} ({self.token.type}) {self.token.lineno}, {self.token.offset}, {self.token.lexpos}"
        )
        self.right.tree(indent + "    ")
