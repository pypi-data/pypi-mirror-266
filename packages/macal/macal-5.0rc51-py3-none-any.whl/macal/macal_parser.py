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

# This is the parser for the Macal language. It is a recursive descent parser.

from __future__ import annotations

import sys
from typing import Any, List, Optional, Tuple

from .ast_node_assignment import AstNodeAssignmentStatement
from .ast_node_binary_expression import AstNodeBinaryExpression
from .ast_node_block import AstNodeBlock
from .ast_node_break_statement import AstNodeBreakStatement
from .ast_node_case_statement import AstNodeCaseStatement
from .ast_node_continue_statement import AstNodeContinueStatement
from .ast_node_default_statement import AstNodeDefaultStatement
from .ast_node_elif_statement import AstNodeElifStatement
from .ast_node_else_statement import AstNodeElseStatement
from .ast_node_expression import AstNodeExpression
from .ast_node_foreach_statement import AstNodeForeachStatement
from .ast_node_function_call_expression import AstNodeFunctionCallExpression
from .ast_node_function_call_statement import AstNodeFunctionCallStatement
from .ast_node_function_definition import AstNodeFunctionDefinition
from .ast_node_function_parameter import AstNodeFunctionParameter
from .ast_node_halt_statement import AstNodeHaltStatement
from .ast_node_if_statement import AstNodeIfStatement
from .ast_node_include_statement import AstNodeIncludeStatement
from .ast_node_indexed_variable_expression import AstNodeIndexedVariableExpression
from .ast_node_istype import AstNodeIsType
from .ast_node_library_expression import AstNodeLibraryExpression
from .ast_node_literal_expression import AstNodeLiteralExpression
from .ast_node_print_statement import AstNodePrintStatement
from .ast_node_program import AstNodeProgram
from .ast_node_return_statement import AstNodeReturnStatement
from .ast_node_select_field import AstNodeSelectField
from .ast_node_select_statement import AstNodeSelectStatement
from .ast_node_switch_statement import AstNodeSwitchStatement
from .ast_node_type_statement import AstNodeTypeStatement
from .ast_node_unary_expression import AstNodeUnaryExpression
from .ast_node_variable_expression import AstNodeVariableExpression
from .ast_node_variable_function_call_expression import (
    AstNodeVariableFunctionCallExpression,
)
from .ast_node_while_statement import AstNodeWhileStatement
from .ast_nodetype import AstNodetype
from .lex_token import LexToken
from .macal_conversions import convertToValue


class Parser:
    def __init__(self, tokens: Optional[List[LexToken]] = None, filename: Optional[str] = None) -> Parser:
        # remove the comments and the whitespace, we don't need that here.
        if tokens is None:
            tokens = []
        self.tokens: List[LexToken] = [
            token for token in tokens if token.token_type != AstNodetype.WHITESPACE and token.token_type != AstNodetype.COMMENT
        ]
        self.filename: str = filename
        self.pos: int = 0
        self.current_token: Optional[LexToken] = None
        if len(self.tokens) > 0:
            self.current_token = self.tokens[self.pos]
        self.node: Optional[AstNodeProgram] = None
        self.do_raise: bool = True

    def error(self, message: str) -> None:
        msg = f"Parser error: {message} in {self.filename} at {self.current_token.lineno}, {self.current_token.offset}"
        if self.do_raise:
            raise Exception(msg)
        else:
            print(msg, file=sys.stderr)
            sys.exit(1)

    def strip_quotes(self, s: str) -> str:
        if (len(s) > 0) and (s[0] == '"' or s[0] == "'"):
            s = s[1:]
        if (len(s) > 0) and (s[-1] == '"' or s[-1] == "'"):
            s = s[:-1]
        return s

    def enforceLiteralType(self, type: AstNodetype, value: Any) -> Any:
        if type == AstNodetype.INTEGER and value != "integer":
            return int(value)
        elif type == AstNodetype.FLOAT and value != "float":
            return float(value)
        elif (
            type in (AstNodetype.STRING, AstNodetype.STRING_INTERPOLATION_STRING_PART, AstNodetype.STRING_INTERPOLATION_END)
            and value != "string"
        ):
            sv = self.strip_quotes(value)
            return sv
        elif type == AstNodetype.BOOLEAN and value != "boolean":
            return bool(value == "true")
        elif type == AstNodetype.NIL and value != "nil":
            return AstNodetype.NIL
        return value

    def get_token(self, index: int) -> LexToken:
        token = self.tokens[index]
        token.value = self.enforceLiteralType(token.token_type, token.value)
        return token

    def advance(self) -> None:
        self.pos += 1
        if self.pos >= len(self.tokens):
            self.current_token = None
        else:
            self.current_token = self.get_token(self.pos)

    def peek(self) -> Optional[LexToken]:
        peek_pos = self.pos + 1
        if peek_pos >= len(self.tokens):
            return None
        else:
            return self.get_token(peek_pos)

    def expect(self, type: AstNodetype) -> Optional[LexToken]:
        token = self.current_token
        if token.token_type == type:
            self.advance()
            return token
        self.error(f"Expected {type} but got {token.token_type}")

    def parse(self) -> AstNodeProgram:
        self.node = self.program()
        return self.node

    def parse_interactive(self, tokens: List[LexToken]) -> AstNodeExpression:
        self.tokens = [
            token for token in tokens if token.token_type != AstNodetype.WHITESPACE and token.token_type != AstNodetype.COMMENT
        ]
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.node = self.program()
        return self.node

    def program(self) -> AstNodeExpression:
        node = AstNodeProgram(self.filename)
        self.block_statement_list(node)
        return node

    def block_statement_list(self, node: AstNodeBlock) -> AstNodeBlock:
        while (
            self.current_token is not None
            and self.current_token.token_type != AstNodetype.RIGHT_BRACE
            and self.current_token.token_type != AstNodetype.EOF
        ):
            if self.current_token.token_type != AstNodetype.EOF:
                node.statements.append(self.statement())
        return node

    def block(self) -> AstNodeBlock:
        node = AstNodeBlock(self.expect(AstNodetype.LEFT_BRACE))
        node = self.block_statement_list(node)
        self.advance()  # skip right brace
        return node

    def statement(self) -> AstNodeExpression:
        if self.current_token.token_type == AstNodetype.IF_STATEMENT:
            return self.if_statement()
        if self.current_token.token_type == AstNodetype.WHILE_STATEMENT:
            return self.while_statement()
        if self.current_token.token_type == AstNodetype.FOREACH_STATEMENT:
            return self.foreach_statement()
        if self.current_token.token_type == AstNodetype.SELECT_STATEMENT:
            return self.select_statement()
        if self.current_token.token_type == AstNodetype.BREAK_STATEMENT:
            return self.break_statement()
        if self.current_token.token_type == AstNodetype.CONTINUE_STATEMENT:
            return self.continue_statement()
        if self.current_token.token_type == AstNodetype.RETURN_STATEMENT:
            return self.return_statement()
        if self.current_token.token_type == AstNodetype.IDENTIFIER:
            return self.assignment_statement()
        if self.current_token.token_type == AstNodetype.LEFT_BRACE:
            return self.block()
        if self.current_token.token_type == AstNodetype.PRINT_STATEMENT:
            return self.print_statement()
        if self.current_token.token_type == AstNodetype.HALT_STATEMENT:
            return self.halt_statement()
        if self.current_token.token_type == AstNodetype.INCLUDE_STATEMENT:
            return self.include_statement()
        if self.current_token.token_type == AstNodetype.SWITCH_STATEMENT:
            return self.switch_statement()
        if self.current_token.token_type == AstNodetype.CONST_STATEMENT:
            return self.const_statement()
        self.error(f"Invalid statement {self.current_token.token_type} {self.current_token.value}")

    def if_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.IF_STATEMENT)
        node = AstNodeIfStatement(token)
        node.condition = self.parse_expression()
        node.block = self.block()
        if self.current_token.token_type == AstNodetype.ELIF_STATEMENT:
            while self.current_token.token_type == AstNodetype.ELIF_STATEMENT:
                node.elif_block_list.append(self.elif_statement())
        if self.current_token.token_type == AstNodetype.ELSE_STATEMENT:
            node.else_block = self.else_statement()
        return node

    def elif_statement(self) -> AstNodeExpression:
        node = AstNodeElifStatement(self.current_token)
        self.advance()
        node.condition = self.parse_expression()
        node.block = self.block()
        return node

    def else_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.advance()
        self.expect(AstNodetype.LEFT_BRACE)
        node = AstNodeElseStatement(token)
        self.block_statement_list(node)
        self.expect(AstNodetype.RIGHT_BRACE)
        return node

    def while_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.WHILE_STATEMENT)
        node = AstNodeWhileStatement(token)
        node.condition = self.parse_expression()
        node.block = self.block()
        return node

    def foreach_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.FOREACH_STATEMENT)
        return AstNodeForeachStatement(token, self.parse_expression(), self.block())

    def select_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.SELECT_STATEMENT)
        distinct = self.current_token.token_type == AstNodetype.DISTINCT_STATEMENT
        if distinct:
            self.advance()
        fields: List[AstNodeSelectField] = []
        while self.current_token.token_type == AstNodetype.IDENTIFIER:
            fieldname = self.current_token
            self.advance()
            alt = None
            if self.current_token.token_type == AstNodetype.AS_STATEMENT:
                self.advance()
                alt = self.current_token
                self.advance()
            fields.append(AstNodeSelectField(fieldname, alt))
            if self.current_token.token_type == AstNodetype.COMMA:
                self.advance()
        if len(fields) == 0 and self.current_token.token_type == AstNodetype.OPERATOR_MULTIPLICATION:
            fields.append(AstNodeSelectField(self.current_token))
            self.advance()
        self.expect(AstNodetype.FROM_STATEMENT)
        from_expr = self.parse_expression()
        where_expr: Optional[AstNodeExpression] = None
        if self.current_token.token_type == AstNodetype.WHERE_STATEMENT:
            self.advance()
            where_expr = self.parse_expression()
        merge = self.current_token.token_type == AstNodetype.MERGE_STATEMENT
        if merge:
            self.advance()
        self.expect(AstNodetype.INTO_STATEMENT)
        into = self.parse_expression()
        if into.expr_type != AstNodetype.VARIABLE_EXPRESSION and into.expr_type != AstNodetype.INDEXED_VARIABLE_EXPRESSION:
            self.error(f"Invalid into expression type {into.expr_type} ({into.line}, {into.column})")
        self.expect(AstNodetype.SEMICOLON)
        return AstNodeSelectStatement(token, fields, from_expr, into, merge, distinct, where_expr)

    def break_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.BREAK_STATEMENT)
        self.expect(AstNodetype.SEMICOLON)
        return AstNodeBreakStatement(token)

    def continue_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.CONTINUE_STATEMENT)
        self.expect(AstNodetype.SEMICOLON)
        return AstNodeContinueStatement(token)

    def return_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.RETURN_STATEMENT)
        node = AstNodeReturnStatement(token)
        if self.current_token.token_type != AstNodetype.SEMICOLON:
            node.expr = self.parse_expression()
        self.expect(AstNodetype.SEMICOLON)
        return node

    def print_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.PRINT_STATEMENT)
        self.expect(AstNodetype.LEFT_PAREN)
        node = AstNodePrintStatement(token, self.expression_list())
        self.expect(AstNodetype.RIGHT_PAREN)
        self.expect(AstNodetype.SEMICOLON)
        return node

    def halt_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.HALT_STATEMENT)
        node = AstNodeHaltStatement(token)
        if self.current_token.token_type != AstNodetype.SEMICOLON:
            node.expr = self.parse_expression()
        self.expect(AstNodetype.SEMICOLON)
        return node

    def is_type_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.advance() # skip the IsType
        self.expect(AstNodetype.LEFT_PAREN)
        var = self.parse_expression()
        self.expect(AstNodetype.RIGHT_PAREN)
        if token.value == "IsString":
            return AstNodeIsType(token, var, AstNodetype.STRING)
        if token.value == "IsInt":
            return AstNodeIsType(token, var, AstNodetype.INTEGER)
        if token.value == "IsFloat":
            return AstNodeIsType(token, var, AstNodetype.FLOAT)
        if token.value == "IsBool":
            return AstNodeIsType(token, var, AstNodetype.BOOLEAN)
        if token.value == "IsRecord":
            return AstNodeIsType(token, var, AstNodetype.RECORD)
        if token.value == "IsArray":
            return AstNodeIsType(token, var, AstNodetype.ARRAY)
        if token.value == "IsFunction":
            return AstNodeIsType(token, var, AstNodetype.FUNCTION)
        if token.value == "IsNil":
            return AstNodeIsType(token, var, AstNodetype.NIL)

    def type_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.TYPE_STATEMENT)
        self.expect(AstNodetype.LEFT_PAREN)
        var = self.parse_expression()
        self.expect(AstNodetype.RIGHT_PAREN)
        return AstNodeTypeStatement(token, var)

    def library_list(self) -> List[AstNodeExpression]:
        token = self.current_token
        self.expect(AstNodetype.IDENTIFIER)
        nodes = [AstNodeLibraryExpression(token)]
        while self.current_token.token_type == AstNodetype.COMMA:
            self.advance()
            token = self.current_token
            self.expect(AstNodetype.IDENTIFIER)
            nodes.append(AstNodeLibraryExpression(token))
        return nodes

    def include_statement(self) -> AstNodeExpression:
        token = self.current_token
        self.expect(AstNodetype.INCLUDE_STATEMENT)
        node = AstNodeIncludeStatement(token, self.library_list())
        self.expect(AstNodetype.SEMICOLON)
        return node

    def switch_statement(self) -> AstNodeExpression:
        token = self.expect(AstNodetype.SWITCH_STATEMENT)
        expr = self.parse_expression()
        if expr.expr_type not in [
            AstNodetype.VARIABLE_EXPRESSION,
            AstNodetype.INDEXED_VARIABLE_EXPRESSION,
            AstNodetype.FUNCTION_CALL_EXPRESSION,
            AstNodetype.VARIABLE_FUNCTION_CALL_EXPRESSION,
        ]:
            # may not need line,col here, but just in case.
            self.error(f"Invalid switch expression type {expr.expr_type} ({expr.line}, {expr.column})")
        node = AstNodeSwitchStatement(token, expr)
        self.expect(AstNodetype.LEFT_BRACE)
        while self.current_token.token_type == AstNodetype.CASE_STATEMENT:
            node.cases.append(self.case_statement())
        if self.current_token.token_type == AstNodetype.DEFAULT_STATEMENT:
            node.default = self.default_statement()
        self.expect(AstNodetype.RIGHT_BRACE)
        return node

    def case_statement(self) -> AstNodeExpression:
        token = self.expect(AstNodetype.CASE_STATEMENT)
        expr = self.parse_expression()
        if expr.expr_type != AstNodetype.LITERAL_EXPRESSION:
            # may not need line,col here, but just in case.
            self.error(f"Invalid case expression type {expr.expr_type} ({expr.line}, {expr.column})")
        node = AstNodeCaseStatement(token, expr)
        self.expect(AstNodetype.COLON)
        node.block = self.block()
        return node

    def default_statement(self) -> AstNodeExpression:
        token = self.expect(AstNodetype.DEFAULT_STATEMENT)
        self.expect(AstNodetype.COLON)
        node = AstNodeDefaultStatement(token)
        node.block = self.block()
        return node

    def expression_list(self) -> List[AstNodeExpression]:
        nodes: List[AstNodeExpression] = []
        if self.current_token.token_type == AstNodetype.RIGHT_PAREN:
            return nodes
        nodes.append(self.parse_expression())
        while self.current_token.token_type == AstNodetype.COMMA:
            self.advance()
            nodes.append(self.parse_expression())
        return nodes

    def expression_array_element(self) -> Any:
        node = self.parse_expression()
        if node.expr_type != AstNodetype.LITERAL_EXPRESSION:
            self.error(
                f"Invalid array element type {node.expr_type} (expected literal, array or record) ({node._token.lineno}, {node._token.offset})"
            )
        vt = node.value_type
        if vt == AstNodetype.STRING_INTERPOLATION_STRING_PART or vt == AstNodetype.STRING_INTERPOLATION_END:
            self.error(
                f"Invalid array element type {vt} (expected literal, array or record) ({node._token.lineno}, {node._token.offset})"
            )
        if vt == AstNodetype.ARRAY or vt == AstNodetype.RECORD:
            return node.value
        return convertToValue(node._token)

    def expression_array(self) -> list:
        if self.current_token.token_type == AstNodetype.RIGHT_BRACKET:
            self.error(f"Invalid array element, expected literal, got ']'")
        array: list = []
        array.append(self.expression_array_element())
        while self.current_token.token_type == AstNodetype.COMMA:
            self.advance()  # skip comma
            array.append(self.expression_array_element())
        return array

    def expression_record_element(self) -> Tuple[Any, Any]:
        key: AstNodeExpression = self.parse_expression()
        if key.expr_type != AstNodetype.LITERAL_EXPRESSION:
            self.error(f"Invalid record key type {key.expr_type} (expected literal) ({key.line}, {key.column})")
        self.expect(AstNodetype.COLON)
        value = self.parse_expression()
        if value.expr_type != AstNodetype.LITERAL_EXPRESSION:
            self.error(
                f"Invalid record value type {value.expr_type} (expected literal, array or record) ({value.line}, {value.column})"
            )
        if (
            key.expr_type == AstNodetype.STRING_INTERPOLATION_STRING_PART
            or key.expr_type == AstNodetype.STRING_INTERPOLATION_END
        ):
            self.error(f"Invalid record key type {key.expr_type} (expected literal) ({key.line}, {key.column})")
        if value.expr_type == AstNodetype.LITERAL_EXPRESSION and (
            value.expr_type == AstNodetype.STRING_INTERPOLATION_STRING_PART
            or value.expr_type == AstNodetype.STRING_INTERPOLATION_END
        ):
            self.error(
                f"Invalid record value type {value.expr_type} (expected literal, array or record) ({value.line}, {value.column})"
            )
        return (key.value, value.value)

    def expression_record(self) -> dict:
        if self.current_token.token_type == AstNodetype.RIGHT_BRACE:
            self.error(f"Invalid record element, expected record key, got '}}' ")
        record: dict = {}
        (key, value) = self.expression_record_element()
        record[key] = value
        while self.current_token.token_type == AstNodetype.COMMA:
            self.advance()  # skip comma
            (key, value) = self.expression_record_element()
            record[key] = value
        return record

    def expect_assign_operand(self) -> LexToken:
        token = self.current_token
        if (
            token.token_type == AstNodetype.OPERATOR_ASSIGNMENT
            or token.token_type == AstNodetype.OPERATOR_ASSIGNMENT_INC
            or token.token_type == AstNodetype.OPERATOR_ASSIGNMENT_DEC
            or token.token_type == AstNodetype.OPERATOR_ASSIGNMENT_MUL
            or token.token_type == AstNodetype.OPERATOR_ASSIGNMENT_DIV
            or token.token_type == AstNodetype.OPERATOR_ASSIGNMENT_POW
            or token.token_type == AstNodetype.OPERATOR_ASSIGNMENT_MOD
            or token.token_type == AstNodetype.OPERATOR_ARROW
        ):
            self.advance()
            return token
        self.error(f"Invalid assignment operator {token.token_type} {token.value} ")

    def assignment_statement(self) -> AstNodeExpression:
        var_expr = self.parse_expression()  # Get the variable as an expression.
        if var_expr.expr_type in [AstNodetype.FUNCTION_CALL_EXPRESSION, AstNodetype.VARIABLE_FUNCTION_CALL_EXPRESSION]:
            self.expect(AstNodetype.SEMICOLON)
            return AstNodeFunctionCallStatement(var_expr._token, var_expr.args)
        if not var_expr.expr_type in [AstNodetype.VARIABLE_EXPRESSION, AstNodetype.INDEXED_VARIABLE_EXPRESSION]:
            self.error(
                f"Invalid assignment statement {var_expr.expr_type} {var_expr._token.value} ({var_expr._token.lineno}, {var_expr._token.offset})"
            )
        if self.current_token.token_type == AstNodetype.LEFT_PAREN:
            self.expect(AstNodetype.LEFT_PAREN)
            args = self.expression_list()
            node = AstNodeFunctionCallStatement(var_expr, args)
            self.expect(AstNodetype.RIGHT_PAREN)
            self.expect(AstNodetype.SEMICOLON)
            return node
        if self.current_token.token_type == AstNodetype.NEW_ARRAY:
            self.advance()
            node = AstNodeAssignmentStatement(var_expr, self.expect_assign_operand(), self.parse_expression())
            node.append = True
            self.expect(AstNodetype.SEMICOLON)
            return node
        op = self.expect_assign_operand()
        if op.token_type == AstNodetype.OPERATOR_ARROW:
            return self.function_definition(var_expr, op)
        assng = AstNodeAssignmentStatement(var_expr, op, self.parse_expression())
        self.expect(AstNodetype.SEMICOLON)
        return assng

    def function_definition(self, var_expr: AstNodeExpression, op: LexToken) -> AstNodeFunctionDefinition:
        params = self.parse_parameter_list()
        return_type = AstNodetype.NIL
        if self.is_type():
            return_type = self.current_token.token_type
            self.advance()
        if self.current_token.token_type == AstNodetype.EXTERNAL_STATEMENT:
            self.advance()
            fndef = AstNodeFunctionDefinition(var_expr, op, params, return_type, None)
            fndef.external = True
            module = self.expect(AstNodetype.STRING)
            fndef.module = self.strip_quotes(module.value)
            self.expect(AstNodetype.COMMA)
            function = self.expect(AstNodetype.STRING)
            fndef.function = self.strip_quotes(function.value)
            self.expect(AstNodetype.SEMICOLON)
            return fndef
        return AstNodeFunctionDefinition(var_expr, op, params, return_type, self.block())

    def const_statement(self) -> AstNodeExpression:
        self.expect(AstNodetype.CONST_STATEMENT)
        var = self.peek()
        result = self.assignment_statement()
        result.const = True
        return result

    def is_type(self) -> bool:
        if self.current_token.token_type in [
            AstNodetype.INTEGER,
            AstNodetype.FLOAT,
            AstNodetype.STRING,
            AstNodetype.BOOLEAN,
            AstNodetype.ARRAY,
            AstNodetype.RECORD,
            AstNodetype.FUNCTION,
            AstNodetype.PARAMS,
            AstNodetype.VARIABLE,
        ]:
            return True
        return False

    def strToType(self, tstr: str) -> AstNodetype:
        if tstr == "integer":
            return AstNodetype.INTEGER
        if tstr == "float":
            return AstNodetype.FLOAT
        if tstr == "string":
            return AstNodetype.STRING
        if tstr == "bool":
            return AstNodetype.BOOLEAN
        if tstr == "array":
            return AstNodetype.ARRAY
        if tstr == "record":
            return AstNodetype.RECORD
        if tstr == "function":
            return AstNodetype.FUNCTION
        if tstr == "params":
            return AstNodetype.PARAMS
        if tstr == "variable":
            return AstNodetype.VARIABLE
        self.error(f"Invalid type {tstr}")

    def parse_parameter_list(self) -> List[AstNodeFunctionParameter]:
        param_list: List[AstNodeFunctionParameter] = []
        self.expect(AstNodetype.LEFT_PAREN)
        while self.current_token.token_type != AstNodetype.RIGHT_PAREN:
            type = AstNodetype.ANY
            if self.is_type():
                type = self.current_token.token_type  # self.strToType(self.current_token.value)
                self.advance()
            ident = self.expect(AstNodetype.IDENTIFIER)
            param_list.append(AstNodeFunctionParameter(ident, type))
            if self.current_token.token_type == AstNodetype.COMMA:
                self.advance()
        self.expect(AstNodetype.RIGHT_PAREN)
        return param_list

    # expression parser

    def parse_expression(self) -> AstNodeExpression:
        expr = self.parse_logical_or()
        return expr

    def parse_logical_or(self) -> AstNodeExpression:
        node = self.parse_logical_and()
        while (
            self.current_token.token_type == AstNodetype.OR_STATEMENT
            or self.current_token.token_type == AstNodetype.XOR_STATEMENT
        ):
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_logical_and())
        return node

    def parse_logical_and(self) -> AstNodeExpression:
        node = self.parse_equality()
        while self.current_token.token_type == AstNodetype.AND_STATEMENT:
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_equality())
        return node

    def parse_equality(self) -> AstNodeExpression:
        node = self.parse_comparison()
        while self.current_token.token_type in [AstNodetype.COMPARETOR_EQUAL, AstNodetype.COMPARETOR_NOT_EQUAL]:
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_comparison())
        return node

    def parse_comparison(self) -> AstNodeExpression:
        node = self.parse_addition()
        while self.current_token.token_type in [
            AstNodetype.COMPARETOR_LESS_THAN,
            AstNodetype.COMPARETOR_LESS_THAN_EQUAL,
            AstNodetype.COMPARETOR_GREATER_THAN,
            AstNodetype.COMPARETOR_GREATER_THAN_EQUAL,
        ]:
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_addition())
        return node

    def parse_addition(self) -> AstNodeExpression:
        node = self.parse_multiplication()
        while self.current_token.token_type in [AstNodetype.OPERATOR_ADDITION, AstNodetype.OPERATOR_SUBTRACTION]:
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_multiplication())
        return node

    def parse_multiplication(self) -> AstNodeExpression:
        node = self.parse_power()
        while self.current_token.token_type in [
            AstNodetype.OPERATOR_MULTIPLICATION,
            AstNodetype.OPERATOR_DIVISION,
            AstNodetype.OPERATOR_MODULUS,
        ]:
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_power())
        return node

    def parse_power(self) -> AstNodeExpression:
        node = self.parse_unary()
        while self.current_token.token_type == AstNodetype.OPERATOR_POWER:
            token = self.current_token
            self.advance()
            node = AstNodeBinaryExpression(token, node, self.parse_unary())
        return node

    def parse_unary(self) -> AstNodeExpression:
        if (
            self.current_token.token_type == AstNodetype.OPERATOR_SUBTRACTION
            or self.current_token.token_type == AstNodetype.OPERATOR_ADDITION
            or self.current_token.token_type == AstNodetype.NOT_STATEMENT
            or self.current_token.token_type == AstNodetype.BITWISE_NOT
        ):
            token = self.current_token
            self.advance()
            return AstNodeUnaryExpression(token, self.parse_primary())
        return self.parse_primary()

    def parse_primary(self) -> AstNodeExpression:
        if self.current_token.token_type == AstNodetype.LEFT_PAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(AstNodetype.RIGHT_PAREN)
            return node
        if self.current_token.token_type == AstNodetype.IDENTIFIER:
            ident = self.current_token
            self.advance()
            node = None            
            if self.current_token.token_type == AstNodetype.LEFT_BRACKET:
                node = AstNodeIndexedVariableExpression(ident)
                while self.current_token.token_type == AstNodetype.LEFT_BRACKET:
                    self.advance()  # skip left bracket
                    node.index.append(self.parse_expression())
                    self.expect(AstNodetype.RIGHT_BRACKET)
                # TODO: Peek ahead to see if it's a function call.
                if self.current_token == AstNodetype.LEFT_PAREN:
                    self.advance()
                    return AstNodeVariableFunctionCallExpression(node, self.expression_list())
                return node
            if self.current_token.token_type == AstNodetype.LEFT_PAREN:
                self.advance()
                if node is None:
                    node = AstNodeFunctionCallExpression(ident, self.expression_list())
                else:
                    node = AstNodeVariableFunctionCallExpression(node, self.expression_list())
                self.expect(AstNodetype.RIGHT_PAREN)
                return node
            # print(ident)
            # print("self.current_token.token_type", self.current_token.token_type, "self.current_token.value", self.current_token.value, "self.current_token.lineno", self.current_token.lineno, "self.current_token.offset", self.current_token.offset)
            return AstNodeVariableExpression(ident)
        if self.current_token.token_type == AstNodetype.INTEGER:
            token = self.current_token
            self.advance()
            return AstNodeLiteralExpression(token)
        if self.current_token.token_type == AstNodetype.FLOAT:
            token = self.current_token
            self.advance()
            return AstNodeLiteralExpression(token)
        if self.current_token.token_type == AstNodetype.STRING:
            token = self.current_token
            self.advance()
            return AstNodeLiteralExpression(token)
        if (
            self.current_token.token_type == AstNodetype.BOOLEAN_FALSE
            or self.current_token.token_type == AstNodetype.BOOLEAN_TRUE
            or self.current_token.token_type == AstNodetype.BOOLEAN
        ):
            token = self.current_token
            self.advance()
            return AstNodeLiteralExpression(token)
        if self.current_token.token_type == AstNodetype.NIL:
            token = self.current_token
            self.advance()
            return AstNodeLiteralExpression(token)
        if self.current_token.token_type == AstNodetype.STRING_INTERPOLATION_START:
            return self.interpolated_string()
        if self.current_token.token_type == AstNodetype.STRING_INTERPOLATION_STRING_PART:
            node = AstNodeLiteralExpression(self.current_token)
            self.advance()
            return node
        if self.current_token.token_type == AstNodetype.NEW_ARRAY or self.current_token.token_type == AstNodetype.ARRAY:
            node = AstNodeLiteralExpression(self.current_token, [], AstNodetype.ARRAY)
            self.advance()
            return node
        if self.current_token.token_type == AstNodetype.NEW_RECORD or self.current_token.token_type == AstNodetype.RECORD:
            node = AstNodeLiteralExpression(self.current_token, {}, AstNodetype.RECORD)
            self.advance()
            return node
        if self.current_token.token_type == AstNodetype.LEFT_BRACKET:
            self.advance()
            node = AstNodeLiteralExpression(self.current_token, self.expression_array(), AstNodetype.ARRAY)
            self.expect(AstNodetype.RIGHT_BRACKET)
            return node
        if self.current_token.token_type == AstNodetype.LEFT_BRACE:
            self.advance()
            node = AstNodeLiteralExpression(self.current_token, self.expression_record(), AstNodetype.RECORD)
            self.expect(AstNodetype.RIGHT_BRACE)
            return node
        if self.current_token.token_type in [
            AstNodetype.IS_ARRAY_STATEMENT,
            AstNodetype.IS_BOOL_STATEMENT,
            AstNodetype.IS_FLOAT_STATEMENT,
            AstNodetype.IS_FUNCTION_STATEMENT,
            AstNodetype.IS_INT_STATEMENT,
            AstNodetype.IS_NIL_STATEMENT,
            AstNodetype.IS_RECORD_STATEMENT,
            AstNodetype.IS_STRING_STATEMENT,
        ]:
            return self.is_type_statement()
        if self.current_token.token_type == AstNodetype.TYPE_STATEMENT:
            return self.type_statement()
        self.error(f"Invalid primary expression {self.current_token.token_type} {self.current_token.value}")

    def interpolated_string(self) -> AstNodeExpression:
        token = LexToken.FromToken(self.current_token)
        self.expect(AstNodetype.STRING_INTERPOLATION_START)
        token.token_type = AstNodetype.OPERATOR_ADDITION
        token.value = "+"
        node = AstNodeBinaryExpression(token, AstNodeLiteralExpression(self.current_token), None)
        self.advance()  # go to right hand side.
        if node.left._token.token_type == AstNodetype.STRING_INTERPOLATION_END:  # if it's just a string without interpolation.
            return node.left
        while self.current_token.token_type != AstNodetype.STRING_INTERPOLATION_END:
            node.right = self.parse_expression()
            node = AstNodeBinaryExpression(token, node, None)
        if self.current_token.token_type == AstNodetype.STRING_INTERPOLATION_END:
            node.right = AstNodeLiteralExpression(self.current_token)
            self.advance()
            return node
        self.error(f"Invalid interpolated string {self.current_token.token_type} {self.current_token.value}")
