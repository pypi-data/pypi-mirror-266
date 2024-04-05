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

# This is the AST Node for the DEFAULT statement

from __future__ import annotations

from typing import Optional

from .ast_node_block import AstNodeBlock
from .ast_node_statement import AstNodeStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeDefaultStatement(AstNodeStatement):
    def __init__(self, token: LexToken) -> AstNodeDefaultStatement:
        super().__init__(token)
        self.expr_type = AstNodetype.DEFAULT_STATEMENT
        self.block: Optional[AstNodeBlock] = None
