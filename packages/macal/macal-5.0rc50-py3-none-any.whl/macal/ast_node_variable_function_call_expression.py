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

# This is the AST node for a function call expression through a variable.

from __future__ import annotations

from typing import List

from .ast_node_expression import AstNodeExpression
from .ast_node_variable_expression import AstNodeVariableExpression
from .ast_nodetype import AstNodetype


class AstNodeVariableFunctionCallExpression(AstNodeExpression):
    def __init__(
        self, variable: AstNodeVariableExpression, args: List[AstNodeExpression]
    ) -> AstNodeVariableFunctionCallExpression:
        super().__init__(variable._token)
        self.expr_type = AstNodetype.VARIABLE_FUNCTION_CALL_EXPRESSION
        self.variable: AstNodeVariableExpression = variable
        self.args: List[AstNodeExpression] = args

    def __str__(self) -> str:
        return f"VariableFunctionCallExpression({self.variable}, {self.args})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}VariableFunctionCallExpression:")
        self.variable.tree(indent + "    ")
        for arg in self.args:
            arg.tree(indent + "    ")
