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

# This is the ast node for the include statement.

from __future__ import annotations

from typing import List

from .ast_node_library_expression import AstNodeLibraryExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeIncludeStatement(AstNodeStatement):
    def __init__(self, token: LexToken, libraries: List[AstNodeLibraryExpression]) -> AstNodeIncludeStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.INCLUDE_STATEMENT
        self.libraries: List[AstNodeLibraryExpression] = libraries

    def __str__(self) -> str:
        return f"IncludeStatement({self.libraries})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}IncludeStatement:")
        for lib in self.libraries:
            lib.tree(indent + "    ")
