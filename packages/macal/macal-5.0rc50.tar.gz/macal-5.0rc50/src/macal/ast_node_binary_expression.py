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

# This is the binary expression node for the AST.

from __future__ import annotations

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeBinaryExpression(AstNodeExpression):
    def __init__(self, op: LexToken, left: AstNodeExpression, right: AstNodeExpression) -> AstNodeBinaryExpression:
        super().__init__(op)
        self.expr_type = AstNodetype.BINARY_EXPRESSION
        self.left: AstNodeExpression = left
        self.right: AstNodeExpression = right
        self.op: LexToken = op

    @property
    def operator(self) -> AstNodeExpression:
        return self._token.value

    def __str__(self) -> str:
        return f"AstNodeExpression({self.left}, {self.op}, {self.right})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}BinaryExpression:")
        print(f"{indent}    {self._token.value} ({self._token.token_type}) {self.line}, {self.column}")
        self.left.tree(indent + "    ")
        self.right.tree(indent + "    ")
