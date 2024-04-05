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

# This is the function call statement node for the AST.

from __future__ import annotations

from typing import Any, List, Optional, Union

from .ast_node_expression import AstNodeExpression
from .ast_node_indexed_variable_expression import AstNodeIndexedVariableExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeFunctionCallStatement(AstNodeStatement):
    def __init__(
        self, ident: Union[LexToken, AstNodeIndexedVariableExpression], args: List[AstNodeExpression]
    ) -> AstNodeFunctionCallStatement:
        self.args: List[AstNodeExpression] = args
        self.index: Optional[List[Any]] = None
        self.var_expr: Optional[AstNodeIndexedVariableExpression] = None
        if isinstance(ident, AstNodeIndexedVariableExpression):
            super().__init__(ident._token)
            self.index = ident.index
            self.var_expr = ident
        else:
            super().__init__(ident)
        self.expr_type = AstNodetype.FUNCTION_CALL

    @property
    def name(self) -> str:
        return self.token.value

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
