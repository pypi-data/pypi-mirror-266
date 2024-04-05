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

# This ast node type is for the IsXXXX type statements.

from __future__ import annotations

from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeIsType(AstNodeStatement):
    def __init__(self, token: LexToken, var: AstNodeExpression, var_type: AstNodetype) -> AstNodeIsType:
        super().__init__(token)
        self.expr_type = AstNodetype.IS_TYPE_STATEMENT
        self.expr: AstNodeExpression = var
        self.TypeToCheck = var_type

    def __str__(self) -> str:
        return f"Is{self.TypeToCheck.name}({self.expr})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}Is{self.TypeToCheck.name}({self.expr})")
