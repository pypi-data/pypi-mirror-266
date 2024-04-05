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

# This is the ast node for the select statement.

from __future__ import annotations

from typing import List, Optional

from .ast_node_expression import AstNodeExpression
from .ast_node_select_field import AstNodeSelectField
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeSelectStatement(AstNodeStatement):
    def __init__(
        self,
        token: LexToken,
        fields: List[AstNodeSelectField],
        from_expr: AstNodeExpression,
        into: AstNodeExpression,
        merge: bool,
        distinct: bool,
        where: Optional[AstNodeExpression] = None,
    ) -> AstNodeSelectStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.SELECT_STATEMENT
        self.Fields: List[AstNodeSelectField] = fields
        self.From: AstNodeExpression = from_expr
        self.Where: Optional[AstNodeExpression] = where
        self.Into: AstNodeExpression = into
        self.merge: bool = merge
        self.distinct: bool = distinct

    def __str__(self) -> str:
        return f"SelectStatement({self.Fields}, {self.From}, {self.Where}, {self.Into})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}SelectStatement:")
        for field in self.Fields:
            field.tree(indent + "    ")
        self.From.tree(indent + "    ")
        if self.Where is not None:
            self.Where.tree(indent + "    ")
        print(f"{indent}    Into: {self.Into.name}")
        print(f"{indent}    Merge: {self.merge}")
        print(f"{indent}    Distinct: {self.distinct}")
