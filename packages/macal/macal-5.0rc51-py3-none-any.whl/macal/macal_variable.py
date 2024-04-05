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

# Compile time variable

from __future__ import annotations
from typing import Any
from .ast_nodetype import AstNodetype

class MacalVariable:
    # scope is a NewVMScope, but we can't import it here because of circular imports.
    def __init__(self, name: str, scope) -> MacalVariable:
        self.name: str = name
        self.value_type: AstNodetype = AstNodetype.NIL
        self.value: Any = AstNodetype.NIL
        self.index: list = []
        self.scope = scope
        self.const = False
        self.arg = False

    @property
    def is_const(self) -> bool:
        return self.const
    
    @property
    def is_indexed(self) -> bool:
        return len(self.index) > 0

    def __str__(self) -> str:
        return f"CTVariable({self.name}, {self.value_type}, {self.value}{' indexed' if self.is_indexed else ''}{' const' if self.is_const else ''}{' arg' if self.arg else ''})"

    def __repr__(self) -> str:
        return self.__str__()
