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

# This is the elif statement ast node.

from __future__ import annotations

from typing import Optional

from .ast_node_block import AstNodeBlock
from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeElifStatement(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeElifStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.ELIF_STATEMENT
        self.condition: Optional[AstNodeExpression] = None
        self.block: AstNodeBlock = AstNodeBlock(token)

    def __str__(self) -> str:
        return f"AstNodeElifStatement({self.condition}, {self.block})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}ElifStatement:")
        self.condition.tree(indent + "    ")
        self.block.tree(indent + "    ")
