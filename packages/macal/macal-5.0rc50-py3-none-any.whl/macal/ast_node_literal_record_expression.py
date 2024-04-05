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

# This is the node object for an record literal expression.

from __future__ import annotations

from .ast_node_literal_expression import AstNodeLiteralExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeLiteralRecordExpression(AstNodeLiteralExpression):
    def __init__(self, token: LexToken, record: dict) -> AstNodeLiteralRecordExpression:
        super().__init__(token)
        self.expr_type = AstNodetype.LITERAL_RECORD_EXPRESSION
        self.record: dict = record

    def tree(self, indent: str = "") -> None:
        print(f"{indent}LiteralRecordExpression:")
        print(f"{indent}  Record:")
        for key, value in self.record.items():
            print(f"    {indent}{key}: {value}")

    @property
    def value(self) -> dict:
        return self.record

    def __str__(self) -> str:
        return f"AstNodeLiteralRecordExpression({self.token})"

    def __repr__(self) -> str:
        return self.__str__()
