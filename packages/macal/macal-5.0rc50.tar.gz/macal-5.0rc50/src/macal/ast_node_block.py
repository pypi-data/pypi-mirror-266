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

# This is a block node for the AST

from __future__ import annotations

from typing import List

from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeBlock(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeBlock:
        super().__init__(token)
        self.expr_type = AstNodetype.BLOCK
        self.statements: List[AstNodeStatement] = []

    def __str__(self) -> str:
        return f"AstNodeBlock({self.statements})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}Block:")
        for statement in self.statements:
            statement.tree(indent + "    ")
