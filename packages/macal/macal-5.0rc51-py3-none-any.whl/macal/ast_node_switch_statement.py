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

# This is the AST node for the SWITCH statment.

from __future__ import annotations

from typing import List, Optional

from .ast_node_case_statement import AstNodeCaseStatement
from .ast_node_default_statement import AstNodeDefaultStatement
from .ast_node_expression import AstNodeExpression
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeSwitchStatement(AstNodeStatement):
    def __init__(self, token: LexToken, expr: AstNodeExpression) -> AstNodeSwitchStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.SWITCH_STATEMENT
        self.expr: AstNodeExpression = expr
        self.cases: List[AstNodeCaseStatement] = []
        self.default: Optional[AstNodeDefaultStatement] = None
