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

# This is the ast node for the library expression.

from __future__ import annotations

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeLibraryExpression(AstNodeExpression):
    def __init__(self, library: LexToken) -> AstNodeLibraryExpression:
        super().__init__(library)
        self.expr_type = AstNodetype.LIBRARY_EXPRESSION
        self.name: str = library.value

    def __str__(self) -> str:
        return f"LibraryExpression({self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}LibraryExpression:")
        print(f"{indent}    {self.name}")
