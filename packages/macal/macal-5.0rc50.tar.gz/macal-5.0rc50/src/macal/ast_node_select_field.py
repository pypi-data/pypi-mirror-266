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

# This is the ast node for a select field.

from __future__ import annotations

from typing import Optional

from .ast_node import AstNode
from .ast_nodetype import AstNodetype
from .lex_token import LexToken


class AstNodeSelectField(AstNode):
    def __init__(self, token: LexToken, alt: Optional[LexToken] = None) -> AstNodeSelectField:
        super().__init__()
        self.expr_type = AstNodetype.SELECT_FIELD
        self.name: str = token.value
        self.token: LexToken = token
        self.altfield: Optional[LexToken] = alt
        if alt is None:
            self.altfield = token
        # good optimization, rather do it here, than having to loop through a dozen of if statements to determine if
        # we need to change the name of the field or not.
        # we now just retrieve the field from the record using the fieldname property, and we write it to the result
        # using the altfieldname property, not caring if it's different or the same.

    @property
    def altfieldname(self) -> Optional[str]:
        if self.altfield is not None:
            return self.altfield.value

    @property
    def fieldname(self) -> str:
        return self.token.value
    
    @property
    def line(self) -> int:
        return self.token.lineno
    
    @property
    def column(self) -> int:
        return self.token.offset

    def __str__(self) -> str:
        return f"SelectField({self.fieldname}{'' if self.altfield is None else f' AS {self.altfieldname}'})"

    def __repr__(self) -> str:
        return self.__str__()

    def tree(self, indent: str = "") -> None:
        print(f"{indent}SelectField: {self.fieldname}{'' if self.altfield is None else f' AS {self.altfieldname}'}")
