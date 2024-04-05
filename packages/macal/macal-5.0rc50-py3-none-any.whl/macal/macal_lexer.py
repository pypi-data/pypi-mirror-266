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

# Lexer class that tokenizes the input string

from __future__ import annotations

from typing import List, Optional

from .ast_nodetype import AstNodetype
from .lex_token import LexToken
from .statement_type_table import StatementTypeTable


class Lexer:
    def __init__(self, text: Optional[str] = None, filename: Optional[str] = None) -> Lexer:
        self.text: Optional[str] = text
        self.pos: int = 0
        if self.text is not None:
            self.current_char: Optional[str] = self.text[self.pos]
        self.lineno: int = 1
        self.offset: int = 1
        self.interpolate_start: bool = False
        self.interpolate_arg_count: int = 0
        self.interpolate_in_arg: bool = False
        self.interpolate_in_string: bool = False
        self.interpolate_terminator: Optional[str] = None
        self.interpolate_part_count: int = 0
        self.filename = filename

    def error(self, msg) -> None:
        message = f"Lexer error: {msg} at line {self.lineno} offset {self.offset} in file {self.filename}"
        raise Exception(msg)

    def advance(self) -> None:
        self.pos += 1
        self.offset += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self) -> Optional[str]:
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]

    def newline(self) -> None:
        if self.current_char == "\n":
            self.lineno += 1
            self.offset = 0

    def get_whitespace_token(self) -> LexToken:
        start = self.pos
        line = self.lineno
        offset = self.offset
        while self.current_char is not None and self.current_char.isspace():
            self.newline()
            self.advance()
        return LexToken(AstNodetype.WHITESPACE, self.text[start : self.pos], line, offset, start, self.filename)

    def get_number_token(self) -> LexToken:
        start = self.pos
        line = self.lineno
        offset = self.offset
        type = AstNodetype.INTEGER
        while self.current_char is not None and self.current_char.isdigit():
            self.advance()
        if self.current_char == ".":
            type = AstNodetype.FLOAT
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                self.advance()
        return LexToken(type, self.text[start : self.pos], line, offset, start, self.filename)

    def do_esc(self, text: str) -> str:
        txt = text.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
        return txt

    def get_string_token(self) -> LexToken:
        start = self.pos
        line = self.lineno
        offset = self.offset
        terminator = self.current_char
        self.advance()
        while self.current_char is not None and self.current_char != terminator:
            self.advance()
        self.advance()
        lexeme = self.do_esc(self.text[start : self.pos])
        return LexToken(AstNodetype.STRING, lexeme, line, offset, start, self.filename)

    def get_identifier_token(self) -> LexToken:
        start = self.pos
        line = self.lineno
        offset = self.offset
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == "_"):
            self.advance()
        identifier = self.text[start : self.pos]
        type = AstNodetype.IDENTIFIER
        if identifier in StatementTypeTable.keys():
            type = StatementTypeTable[identifier]
        return LexToken(type, identifier, line, offset, start, self.filename)

    def get_short_comment_token(self) -> LexToken:
        start = self.pos
        line = self.lineno
        offset = self.offset
        while self.current_char is not None and self.current_char != "\n":
            self.advance()
        return LexToken(AstNodetype.COMMENT, self.text[start : self.pos], line, offset, start, self.filename)

    def strip_long_comment_text(self, text: str) -> str:
        return text.replace("\r", " ").replace("\n", " ").replace("\t", "    ")

    def get_long_comment_token(self) -> LexToken:
        start = self.pos
        line = self.lineno
        offset = self.offset
        self.advance()  # skip /
        self.advance()  # skip *
        while self.current_char is not None:
            self.newline()
            self.advance()
            if self.current_char == "*" and self.peek() == "/":
                break
        self.advance()  # skip *
        self.advance()  # skip /
        return LexToken(AstNodetype.COMMENT, self.strip_long_comment_text(self.text[start : self.pos]), line, offset, start, self.filename)

    def get_string_interpolation_str_token(self, start, line, offset) -> LexToken:
        # this gets the string up until the next interpolation token.
        while (
            self.current_char is not None
            and self.current_char != self.interpolate_terminator
            and (self.current_char != "{" or (self.current_char == "{" and self.peek() == "{"))
        ):
            self.newline()
            self.advance()
        if self.current_char == self.interpolate_terminator:
            self.interpolate_in_string = False
            self.advance()
            value = self.text[start : self.pos]
            if not value.startswith(self.interpolate_terminator):
                value = self.interpolate_terminator + value
            return LexToken(AstNodetype.STRING_INTERPOLATION_END, value, line, offset, start, self.filename)
        if self.current_char == "{":  # next we expect expressions
            self.interpolate_in_arg = True
            self.advance()
            value = self.text[start : self.pos - 1]  # skip the {
            if not value.startswith(self.interpolate_terminator):
                value = self.interpolate_terminator + value
            if not value.endswith(self.interpolate_terminator):
                value = value + self.interpolate_terminator
            return LexToken(AstNodetype.STRING_INTERPOLATION_STRING_PART, value, line, offset, start, self.filename)
        self.error(f"Invalid string interpolation")

    def get_string_interpolation_start_token(self) -> LexToken:
        if self.current_char != '"' and self.current_char != "'":
            self.error(f"Expected ' or \", got {self.current_char}")
        self.interpolate_start = False
        self.interpolate_in_string = True
        self.interpolate_terminator = self.current_char
        start = self.pos
        line = self.lineno
        offset = self.offset
        self.advance()  # skip the string terminator.
        return self.get_string_interpolation_str_token(start, line, offset)

    def get_next_token(self) -> LexToken:
        cur = self.current_char
        if cur is None:
            return LexToken(AstNodetype.EOF, "", self.lineno, self.offset, self.pos, self.filename)
        if self.interpolate_start:
            return self.get_string_interpolation_start_token()
        if self.interpolate_in_string and not self.interpolate_in_arg:
            return self.get_string_interpolation_str_token(self.pos, self.lineno, self.offset)
        if self.interpolate_in_string and self.interpolate_in_arg and cur == "}":
            self.interpolate_in_arg = False
            self.interpolate_arg_count += 1
            self.advance()
            return self.get_string_interpolation_str_token(self.pos, self.lineno, self.offset)
        if cur.isspace():
            return self.get_whitespace_token()
        if cur.isdigit():
            return self.get_number_token()
        if cur == '"' or self.current_char == "'":
            return self.get_string_token()
        if cur == "/" and self.peek() == "/":
            return self.get_short_comment_token()
        if cur == "#":
            return self.get_short_comment_token()
        if cur == "/" and self.peek() == "*":
            return self.get_long_comment_token()
        if cur.isalpha() or self.current_char == "_":
            return self.get_identifier_token()
        if cur == "+":
            self.advance()
            if self.current_char == "+":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_INCREMENT, "++", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            elif self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ASSIGNMENT_INC, "+=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_ADDITION, "+", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "-":
            self.advance()
            if self.current_char == "-":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_DECREMENT, "--", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            elif self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ASSIGNMENT_DEC, "-=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_SUBTRACTION, "-", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "*":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ASSIGNMENT_MUL, "*=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_MULTIPLICATION, "*", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "/":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ASSIGNMENT_DIV, "/=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_DIVISION, "/", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "^":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ASSIGNMENT_POW, "^=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_POWER, "^", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "%":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ASSIGNMENT_MOD, "%=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_MODULUS, "%", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "=":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.COMPARETOR_EQUAL, "==", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            if self.current_char == ">":
                self.advance()
                return LexToken(AstNodetype.OPERATOR_ARROW, "=>", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.OPERATOR_ASSIGNMENT, "=", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "<":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.COMPARETOR_LESS_THAN_EQUAL, "<=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.COMPARETOR_LESS_THAN, "<", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == ">":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.COMPARETOR_GREATER_THAN_EQUAL, ">=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.COMPARETOR_GREATER_THAN, ">", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "!":
            self.advance()
            if self.current_char == "=":
                self.advance()
                return LexToken(AstNodetype.COMPARETOR_NOT_EQUAL, "!=", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.NOT_STATEMENT, "!", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "&":
            self.advance()
            if self.current_char == "&":
                self.advance()
                return LexToken(AstNodetype.AND_STATEMENT, "&&", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.BITWISE_AND, "&", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "|":
            self.advance()
            if self.current_char == "|":
                self.advance()
                return LexToken(AstNodetype.OR_STATEMENT, "||", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.BITWISE_OR, "|", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "~":
            self.advance()
            return LexToken(AstNodetype.BITWISE_NOT, "~", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "(":
            self.advance()
            return LexToken(AstNodetype.LEFT_PAREN, "(", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == ")":
            self.advance()
            return LexToken(AstNodetype.RIGHT_PAREN, ")", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "[":
            self.advance()
            if self.current_char == "]":
                self.advance()
                return LexToken(AstNodetype.NEW_ARRAY, "[]", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.LEFT_BRACKET, "[", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "]":
            self.advance()
            return LexToken(AstNodetype.RIGHT_BRACKET, "]", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "{":
            self.advance()
            if self.current_char == "}":
                self.advance()
                return LexToken(AstNodetype.NEW_RECORD, "{}", self.lineno, self.offset - 2, self.pos - 2, self.filename)
            return LexToken(AstNodetype.LEFT_BRACE, "{", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "}":
            self.advance()
            return LexToken(AstNodetype.RIGHT_BRACE, "}", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == ",":
            self.advance()
            return LexToken(AstNodetype.COMMA, ",", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == ":":
            self.advance()
            return LexToken(AstNodetype.COLON, ":", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == ";":
            self.advance()
            return LexToken(AstNodetype.SEMICOLON, ";", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == ".":
            self.advance()
            return LexToken(AstNodetype.DOT, ".", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        if cur == "$":
            self.advance()
            self.interpolate_start = True
            return LexToken(AstNodetype.STRING_INTERPOLATION_START, "$", self.lineno, self.offset - 1, self.pos - 1, self.filename)
        self.error(f"Invalid character {self.current_char}")

    def tokenize(self) -> List[LexToken]:
        if self.text is None:
            return []
        tokens = []
        token = self.get_next_token()
        while token.token_type != AstNodetype.EOF:
            if token is not None:
                tokens.append(token)
            token = self.get_next_token()
        tokens.append(token)  # EOF
        return tokens

    def lex(self, text: str) -> List[LexToken]:
        if text is None:
            return []
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.lineno = 1
        self.offset = 1
        self.interpolate_start = False
        self.interpolate_arg_count = 0
        self.interpolate_in_arg = False
        self.interpolate_in_string = False
        self.interpolate_terminator = None
        self.interpolate_part_count = 0
        return self.tokenize()
