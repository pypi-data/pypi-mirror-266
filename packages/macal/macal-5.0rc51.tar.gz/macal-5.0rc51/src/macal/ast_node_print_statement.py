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

# This is the ast node for the print statement.

from __future__ import annotations

from typing import List

from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodePrintStatement(AstNodeStatement):
    def __init__(self, token: LexToken, args: List[AstNodeExpression]) -> AstNodePrintStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.PRINT_STATEMENT
        self.args: List[AstNodeExpression] = args

    def __str__(self) -> str:
        return f"PrintStatement({self.args})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}PrintStatement:")
        for arg in self.args:
            arg.tree(indent + "    ")
