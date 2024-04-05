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

# This is the if statement AST node.

from __future__ import annotations

from typing import List, Optional

from .ast_node_block import AstNodeBlock
from .ast_node_elif_statement import AstNodeElifStatement
from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeIfStatement(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeIfStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.IF_STATEMENT
        self.condition: Optional[AstNodeExpression] = None
        self.block: Optional[AstNodeBlock] = None
        self.elif_block_list: List[AstNodeElifStatement] = []
        self.else_block: Optional[AstNodeBlock] = None

    def __str__(self) -> str:
        return f"AstNodeIfStatement({self.condition}, {self.block}, {self.elif_block_list} {self.else_block})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}IfStatement:")
        self.condition.tree(indent + "    ")
        self.block.tree(indent + "    ")
        for elif_statement in self.elif_block_list:
            elif_statement.tree(indent + "    ")
        if self.else_block:
            self.else_block.tree(indent + "    ")
