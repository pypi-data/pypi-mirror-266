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

# This is the AST Node for the CASE statement

from __future__ import annotations

from typing import Optional

from .ast_node_block import AstNodeBlock
from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken
from .macal_conversions import convertToValue


class AstNodeCaseStatement(AstNodeStatement):
    def __init__(self, token: LexToken, expr: AstNodeExpression) -> AstNodeCaseStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.CASE_STATEMENT
        self.expr: AstNodeExpression = expr
        self.block: Optional[AstNodeBlock] = None

    def case_value(self):
        return convertToValue(self.expr._token)
