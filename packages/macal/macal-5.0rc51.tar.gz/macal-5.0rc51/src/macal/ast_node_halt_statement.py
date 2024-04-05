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

# This is the ast node for the halt statement.

from __future__ import annotations

from typing import Optional

from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeHaltStatement(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeHaltStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.HALT_STATEMENT
        self.expr: Optional[AstNodeExpression] = None

    def __str__(self) -> str:
        return f"HaltStatement({self.expr})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}HaltStatement:")
        self.expr.tree(indent + "    ")
