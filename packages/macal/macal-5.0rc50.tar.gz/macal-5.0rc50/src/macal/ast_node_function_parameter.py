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

# function argument definition node

from __future__ import annotations

from .ast_node import AstNode
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeFunctionParameter(AstNode):
    def __init__(self, token: LexToken, type: AstNodetype) -> AstNodeFunctionParameter:
        super().__init__()
        self.token: LexToken = token
        self.node_type: AstNodetype = type

    @property
    def name(self) -> str:
        return self.token.value

    def __str__(self) -> str:
        return f"AstNodeFunctionParameter({self.name}:{self.node_type.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}{self.__str__()}")
