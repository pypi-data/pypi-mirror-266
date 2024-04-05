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


# This is the ast node for the while statement.

from __future__ import annotations

from typing import Optional

from .ast_node_block import AstNodeBlock
from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeWhileStatement(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeWhileStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.WHILE_STATEMENT
        self.condition: Optional[AstNodeExpression] = None
        self.block: Optional[AstNodeBlock] = None

    def __str__(self) -> str:
        return f"WhileStatement({self.condition}, {self.block})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}WhileStatement:")
        if self.condition is not None:
            self.condition.tree(indent + "    ")
        if self.block is not None:
            self.block.tree(indent + "    ")
