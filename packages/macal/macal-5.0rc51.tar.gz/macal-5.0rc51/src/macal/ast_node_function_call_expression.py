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

# This is the function call expression node for the AST.

from __future__ import annotations

from typing import List

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeFunctionCallExpression(AstNodeExpression):
    def __init__(self, token: LexToken, args: List[AstNodeExpression]) -> AstNodeFunctionCallExpression:
        super().__init__(token)
        self.expr_type = AstNodetype.FUNCTION_CALL_EXPRESSION
        self.args: List[AstNodeExpression] = args

    @property
    def name(self) -> str:
        return self._token.value

    def __str__(self) -> str:
        return f"AstNodeFunctionCallExpression({self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}{self}")
        if self.args:
            for arg in self.args:
                arg.tree(indent + "    ")
        else:
            print()
