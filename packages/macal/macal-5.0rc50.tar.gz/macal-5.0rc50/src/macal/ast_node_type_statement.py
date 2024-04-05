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

# This ast node type is for the Type statement.

from __future__ import annotations

from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeTypeStatement(AstNodeStatement):
    def __init__(self, token: LexToken, var: AstNodeExpression):
        super().__init__(token)
        self.expr_type = AstNodetype.TYPE_STATEMENT
        self.expr: AstNodeExpression = var

    def __str__(self):
        return f"Type({self.expr})"

    def __repr__(self):
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}Type({self.expr})")
