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

# function definition node for ast tree

from __future__ import annotations

from typing import List

from .ast_node import AstNode
from .ast_node_block import AstNodeBlock
from .ast_node_function_parameter import AstNodeFunctionParameter
from .ast_node_variable_expression import AstNodeVariableExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeFunctionDefinition(AstNode):
    def __init__(
        self,
        var_expr: AstNodeVariableExpression,
        op: LexToken,
        parameters: List[AstNodeFunctionParameter],
        return_type: AstNodetype,
        body: AstNodeBlock,
    ) -> AstNodeFunctionDefinition:
        super().__init__()
        self.expr_type = AstNodetype.FUNCTION_DEFINITION
        self.return_type: AstNodetype = return_type
        self.var_expr: AstNodeVariableExpression = var_expr
        self.op: LexToken = op
        self.parameters: List[AstNodeFunctionParameter] = parameters
        self.body: AstNodeBlock = body
        self.external: bool = False
        self.module: str = ""
        self.function: str = ""

    @property
    def name(self) -> str:
        return self.var_expr.name

    @property
    def line(self) -> int:
        return self.var_expr.line

    @property
    def column(self) -> int:
        return self.var_expr.column

    @property
    def returns(self) -> bool:
        return self.return_type != AstNodetype.NIL

    def __str__(self) -> str:
        pl = [param.__str__() for param in self.parameters]
        return f"AstNodeFunctionDefinition({self.name}({', '.join(pl)})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}{self}")
        if self.external:
            print(f"{indent}    external: {self.module}.{self.function}")
        else:
            self.body.tree(indent + "    ")
