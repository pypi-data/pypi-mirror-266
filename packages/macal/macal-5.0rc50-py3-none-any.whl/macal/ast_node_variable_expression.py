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

# This is the variable access node for the AST.

from __future__ import annotations

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeVariableExpression(AstNodeExpression):
    def __init__(self, variable: LexToken) -> AstNodeVariableExpression:
        super().__init__(variable)
        self.expr_type = AstNodetype.VARIABLE_EXPRESSION

    @property
    def name(self) -> str:
        return self._token.value

    @property
    def variable(self) -> LexToken:
        return self._token

    def __str__(self) -> str:
        return f"AstNodeVariableExpression({self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = ""):
        print(f"{indent}AstNodeVariableExpression:")
        print(f"{indent}    {self.name} {self.line}, {self.column}")
