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


# AST Node base class

from __future__ import annotations

from .ast_nodetype import AstNodetype


class AstNode:
    def __init__(self) -> AstNode:
        self.expr_type: AstNodetype = AstNodetype.UNDEFINED

    def __str__(self) -> str:
        return f"AstNode()"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}AstNode:")
        print(f"{indent}    {self.expr_type}")
