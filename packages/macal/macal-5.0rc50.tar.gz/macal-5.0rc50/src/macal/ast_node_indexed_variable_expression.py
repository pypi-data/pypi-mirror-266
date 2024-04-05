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

# This is the indexed variable access node for the AST.

from __future__ import annotations

from typing import List

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeIndexedVariableExpression(AstNodeExpression):
    def __init__(self, token: LexToken) -> AstNodeIndexedVariableExpression:
        super().__init__(token)
        self.expr_type = AstNodetype.INDEXED_VARIABLE_EXPRESSION
        self.name: LexToken = token.value
        self.index: List[AstNodeExpression] = []

    def __str__(self) -> str:
        return f"AstNodeIndexedVariableExpression({self.name}, {self.index})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}AstNodeIndexedVariableExpression:")
        print(f"{indent}    {self.name}{self.index}")
