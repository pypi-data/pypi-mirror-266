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

# This is the statement node for the AST.

from __future__ import annotations

from .ast_node import AstNode
from .lex_token import LexToken


class AstNodeStatement(AstNode):
    def __init__(self, token: LexToken) -> AstNodeStatement:
        super().__init__()
        self.token: LexToken = token
        self.expr_type = token.token_type

    @property
    def name(self) -> str:
        return self.token.value

    @property
    def line(self) -> int:
        return self.token.lineno

    @property
    def column(self) -> int:
        return self.token.offset

    def __str__(self) -> str:
        return f"AstNodeStatement({self.expr_type}, {self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}Statement({self.expr_type}, {self.name})")
