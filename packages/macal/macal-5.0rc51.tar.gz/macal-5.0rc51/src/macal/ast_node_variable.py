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

# This is the ast node for a variable

from __future__ import annotations

from typing import Optional

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeVariable(AstNodeExpression):
    def __init__(self, token: LexToken) -> AstNodeVariable:
        super().__init__(token)
        self.expr_type = AstNodetype.VARIABLE
        self.name: str = token.value
        self.value: Optional[AstNodeExpression] = None

    def __str__(self) -> str:
        return f"AstNodeVariable({self.name}, {self.value})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}Variable:")
        print(f"{indent}    {self.name}")
        if self.value is not None:
            self.value.tree(indent + "    ")
