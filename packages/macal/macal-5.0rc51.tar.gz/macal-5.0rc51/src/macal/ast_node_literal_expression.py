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

# This is the expression node for the AST.

from __future__ import annotations

from typing import Any, Optional

from .ast_node_expression import AstNodeExpression
from .ast_nodetype import AstNodetype
from .lex_token import LexToken
from .macal_conversions import convertToValue


class AstNodeLiteralExpression(AstNodeExpression):
    def __init__(
        self, token: LexToken, value: Optional[Any] = None, value_type: AstNodetype = AstNodetype.NIL
    ) -> AstNodeLiteralExpression:
        super().__init__(token)
        self.expr_type = AstNodetype.LITERAL_EXPRESSION
        if value is None:
            self._value: Optional[Any] = token.value
            self._value_type: AstNodetype = token.token_type
        else:
            self._value: Optional[Any] = value
            self._value_type: AstNodetype = value_type
        if self._value_type == AstNodetype.BOOLEAN:
            self._value = self._value == "true" or self._value is True

    def __str__(self) -> str:
        return f"AstNodeExpression({self._token})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def value(self) -> Any:
        if self._value is not None:
            return self._value
        return convertToValue(self._token)

    @property
    def value_type(self) -> AstNodetype:
        return self._value_type

    def tree(self, indent: str = "") -> None:
        print(f"{indent}LiteralExpression:")
        print(f"{indent}    {self.value} ({self._token.token_type})")
