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

# This is the ast node for assigning a value to a variable.

from __future__ import annotations

from typing import Union

from .ast_node import AstNode
from .ast_node_expression import AstNodeExpression
from .ast_node_literal_expression import AstNodeLiteralExpression
from .ast_node_statement import AstNodeStatement
from .ast_node_variable_expression import AstNodeVariableExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


# This is now almost identical to a binary expression, except that the lhs is known to be a variable expression.
class AstNodeAssignmentStatement(AstNodeStatement):
    def __init__(
        self, var_expr: AstNodeVariableExpression, op: LexToken, expr: AstNodeExpression
    ) -> AstNodeAssignmentStatement:
        super().__init__(var_expr._token)
        self.expr_type = AstNodetype.ASSIGNMENT_STATEMENT
        self.lhs = var_expr
        self.variable_name: str = var_expr.name
        self.op: LexToken = op
        self.rhs: Union[AstNodeLiteralExpression, AstNodeExpression]
        if isinstance(expr, list):
            self.rhs = AstNodeLiteralExpression(LexToken(AstNodetype.ARRAY, expr, 0, 0, 0), expr, AstNodetype.ARRAY)
        elif isinstance(expr, dict):
            self.rhs = AstNodeLiteralExpression(LexToken(AstNodetype.RECORD, expr, 0, 0, 0), expr, AstNodetype.RECORD)
        else:
            self.rhs: AstNodeExpression = expr
        self.append: bool = False
        self.const: bool = False

    @property
    def operator(self) -> str:
        return self.op.value

    def __str__(self) -> str:
        return f"AstNodeAssignmentStatement({self.variable_name}, {self.op}, {self.lhs} {self.rhs})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}AssignmentStatement():")
        self.lhs.tree(indent + "    ")
        print(f"{indent}    {self.op}")
        if isinstance(self.rhs, AstNode):
            self.rhs.tree(indent + "    ")
        else:
            print(indent, "    ", self.rhs)
