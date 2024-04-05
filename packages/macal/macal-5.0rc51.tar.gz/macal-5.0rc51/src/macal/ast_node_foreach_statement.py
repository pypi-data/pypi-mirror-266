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

# This is the ast node for the foreach statement.

from __future__ import annotations

from .ast_node_block import AstNodeBlock
from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeForeachStatement(AstNodeStatement):
    def __init__(self, token: LexToken, expr: AstNodeExpression, block: AstNodeBlock) -> AstNodeForeachStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.FOREACH_STATEMENT
        self.expr: AstNodeExpression = expr
        self.block: AstNodeBlock = block

    def __str__(self) -> str:
        return f"ForeachStatement({self.expr}, {self.block})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}ForeachStatement:")
        self.expr.tree(indent + "    ")
        self.block.tree(indent + "    ")
