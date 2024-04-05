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

# This is the expression ast node.

from __future__ import annotations

from .ast_node import AstNode
from .ast_nodetype import AstNodetype
from .lex_token import LexToken

class AstNodeExpression(AstNode):
    def __init__(self, token: LexToken) -> AstNodeExpression:
        super().__init__()
        self._token: LexToken = token
        self.expr_type = AstNodetype.EXPRESSION

    @property
    def line(self) -> int:
        return self._token.lineno

    @property
    def column(self) -> int:
        return self._token.offset

    @property
    def token_value(self) -> str:
        return self._token.value

    def __str__(self) -> str:
        return f"AstNodeExpression({self._token})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}{self}")
