# -*- coding: utf-8 -*-
#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      2023-10-24
#
# Copyright 2023 Westcon-Comstor
#

# This is the new Macal Compiler, it will compile the AST from the parser into "bytecode" for the VM.

from __future__ import annotations

import os
import sys
from typing import Optional

from .ast_node_assignment import AstNodeAssignmentStatement
from .ast_node_binary_expression import AstNodeBinaryExpression
from .ast_node_block import AstNodeBlock
from .ast_node_break_statement import AstNodeBreakStatement
from .ast_node_case_statement import AstNodeCaseStatement
from .ast_node_continue_statement import AstNodeContinueStatement
from .ast_node_elif_statement import AstNodeElifStatement
from .ast_node_expression import AstNodeExpression
from .ast_node_foreach_statement import AstNodeForeachStatement
from .ast_node_function_call_statement import AstNodeFunctionCallStatement
from .ast_node_function_call_expression import AstNodeFunctionCallExpression
from .ast_node_function_definition import AstNodeFunctionDefinition
from .ast_node_halt_statement import AstNodeHaltStatement
from .ast_node_if_statement import AstNodeIfStatement
from .ast_node_istype import AstNodeIsType
from .ast_node_include_statement import AstNodeIncludeStatement
from .ast_node_indexed_variable_expression import AstNodeIndexedVariableExpression
from .ast_node_literal_expression import AstNodeLiteralExpression
from .ast_node_print_statement import AstNodePrintStatement
from .ast_node_program import AstNodeProgram
from .ast_node_return_statement import AstNodeReturnStatement
from .ast_node_select_statement import AstNodeSelectStatement
from .ast_node_statement import AstNodeStatement
from .ast_node_switch_statement import AstNodeSwitchStatement
from .ast_node_type_statement import AstNodeTypeStatement
from .ast_node_unary_expression import AstNodeUnaryExpression
from .ast_node_variable_expression import AstNodeVariableExpression
from .ast_node_variable_function_call_expression import (
    AstNodeVariableFunctionCallExpression,
)
from .ast_node_while_statement import AstNodeWhileStatement
from .ast_nodetype import AstNodetype
from .config import SearchPath
from .macal_compiler_scope import NewScope
from .macal_lexer import Lexer
from .macal_opcode import *
from .macal_parser import Parser
from .macal_variable import MacalVariable


class MacalCompiler:
    def __init__(self, verbose: bool):
        self.program: Optional[AstNodeProgram] = None
        self.output: str = None
        self.verbose: bool = verbose
        self.reserved: list[str] = []
        self.filename: str = None
        self.do_raise: bool = False

    def _error(self, message: str) -> None:
        msg = f"Compiler exception: {message} in {self.filename}"
        if self.do_raise:
            self._error(msg)
        else:
            print(msg, file=sys.stderr)
            sys.exit(1)

    def Compile(self, program: AstNodeProgram, reserved: list[str]) -> list:
        self.program = program
        self.reserved = reserved
        self.filename = program.filename
        scope = NewScope("root")
        instructions = []
        for var in reserved:
            scope.new_variable(var.strip())
        self._compile_program(self.program, scope, instructions)
        instructions.append(
            (Opcode_HALT, [(Opcode_LOAD_CONSTANT, 0)])
        )  # not really needed, but for clarity and completeness.
        if self.verbose:
            for instruction in instructions:
                print(instruction[0], " ", instruction[1:])
        return instructions

    def _compile_program(
        self, program: AstNodeProgram, scope: NewScope, instructions: list
    ):
        for statement in program.statements:
            self._compile_statement(statement, scope, instructions)

    def _compile_statement(
        self, statement: AstNodeStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type == AstNodetype.ASSIGNMENT_STATEMENT:
            self._compile_assignment_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.PRINT_STATEMENT:
            self._compile_print_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.FUNCTION_DEFINITION:
            self._compile_function_definition(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.RETURN_STATEMENT:
            self._compile_return_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.FUNCTION_CALL:
            self._compile_function_call_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.FUNCTION_CALL_EXPRESSION:
            self._compile_function_call_expression(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.HALT_STATEMENT:
            self._compile_halt_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.BREAK_STATEMENT:
            self._compile_break_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.CONTINUE_STATEMENT:
            self._compile_continue_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.IF_STATEMENT:
            self._compile_if_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.WHILE_STATEMENT:
            self._compile_while_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.FOREACH_STATEMENT:
            self._compile_foreach_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.SWITCH_STATEMENT:
            self._compile_switch_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.INCLUDE_STATEMENT:
            self._compile_include_statement(statement, scope, instructions)
        elif statement.expr_type == AstNodetype.SELECT_STATEMENT:
            self._compile_select_statement(statement, scope, instructions)
        else:
            self._error(
                f"Unknown statement type {statement.expr_type} @ {statement.line}:{statement.column}"
            )

    def _compile_block(
        self, statement: AstNodeBlock, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.BLOCK:
            self._error(
                f"Expected block, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        for statement in statement.statements:
            self._compile_statement(statement, scope, instructions)

    # statement fucntions

    def _compile_print_statement(
        self, statement: AstNodePrintStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.PRINT_STATEMENT:
            self._error(
                f"Expected print statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        args = []
        for arg in statement.args:
            self._compile_expression(arg, scope, args)
        instructions.append((Opcode_PRINT, len(statement.args), args))

    def _compile_function_definition(
        self, statement: AstNodeFunctionDefinition, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.FUNCTION_DEFINITION:
            self._error(
                f"Expected function definition, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        child = scope.new_child(statement.name)
        scope.functions.append(child)
        child.is_function = True
        params = []
        for param in statement.parameters:
            params.append((Opcode_NEW_VARIABLE, param.name))
            child.variables.append(MacalVariable(param.name, child))

        fndef = None
        if statement.body is not None:
            blk = []
            self._compile_block(statement.body, child, blk)
            fndef = (Opcode_FUNCTION_DEFINITION, child.name, params, blk)

        if statement.external:
            fndef = (
                Opcode_EXTERN_FUNCTION_DEFINITION,
                statement.name,
                params,
                statement.module,
                statement.function,
            )
            child.is_extern_function_definition = True

        if fndef is None:
            self._error(
                f"Function definition without body @ {statement.line}:{statement.column}"
            )

        child.function_definition.append(fndef)
        instructions.append(fndef)

    def _compile_assignment_statement(
        self, statement: AstNodeAssignmentStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.ASSIGNMENT_STATEMENT:
            self._error(
                f"Expected assignment statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        var = scope.get_variable(statement.lhs.name)
        new_var = False
        if var is None:
            instructions.append((Opcode_NEW_VARIABLE, statement.lhs.name))
            scope.variables.append(MacalVariable(statement.lhs.name, scope))
            new_var = True
        lhs = []
        self._compile_expression(statement.lhs, scope, lhs)
        op = statement.operator
        rhs = []
        self._compile_expression(statement.rhs, scope, rhs)
        if op == "=":
            instructions.append((Opcode_STORE_VARIABLE, lhs, rhs, statement.append))
            return
        if statement.append:
            self._error(
                f"Operator {op} not supported for append to array @ {statement.line}:{statement.column}"
            )
        if new_var:
            self._error(
                f"Operator {op} not supported for new variable @ {statement.line}:{statement.column}"
            )
        opcode = 0
        if op == "+=":
            opcode = Opcode_ADD
        elif op == "-=":
            opcode = Opcode_SUB
        elif op == "*=":
            opcode = Opcode_MUL
        elif op == "/=":
            opcode = Opcode_DIV
        elif op == "%=":
            opcode = Opcode_MOD
        elif op == "^=":
            opcode = Opcode_POW
        else:
            self._error(
                f"Unknown assignment operator {op} @ {statement.line}:{statement.column}"
            )
        instructions.append((Opcode_STORE_VARIABLE, lhs, [(opcode, lhs, rhs)]))

    def _compile_return_statement(
        self, statement: AstNodeReturnStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.RETURN_STATEMENT:
            self._error(
                f"Expected return statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        value = []
        if statement.expr is not None:
            self._compile_expression(statement.expr, scope, value)
        instructions.append((Opcode_RET, value))

    def _compile_halt_statement(
        self, statement: AstNodeHaltStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.HALT_STATEMENT:
            self._error(
                f"Expected halt statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        value = []
        if statement.expr is not None:
            self._compile_expression(statement.expr, scope, value)
        instructions.append((Opcode_HALT, value))

    def _compile_break_statement(
        self, statement: AstNodeBreakStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.BREAK_STATEMENT:
            self._error(
                f"Expected break statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        instructions.append((Opcode_BREAK,))

    def _compile_continue_statement(
        self, statement: AstNodeContinueStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.CONTINUE_STATEMENT:
            self._error(
                f"Expected continue statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        instructions.append((Opcode_CONTINUE,))

    def _compile_if_statement(
        self, statement: AstNodeIfStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.IF_STATEMENT:
            self._error(
                f"Expected if statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.condition, scope, expr)
        blk = []
        self._compile_block(statement.block, scope, blk)
        elifs = []
        for elif_statement in statement.elif_block_list:
            self._compile_elif_statement(elif_statement, scope, elifs)
        elseblk = []
        if statement.else_block is not None:
            block = statement.else_block
            block.expr_type = AstNodetype.BLOCK
            self._compile_block(statement.else_block, scope, elseblk)
        instructions.append((Opcode_IF, expr, blk, elifs, (Opcode_ELSE, elseblk)))

    def _compile_elif_statement(
        self, statement: AstNodeElifStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.ELIF_STATEMENT:
            self._error(
                f"Expected elif statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.condition, scope, expr)
        blk = []
        self._compile_block(statement.block, scope, blk)
        instructions.append((Opcode_ELIF, expr, blk))

    def _compile_foreach_statement(
        self, statement: AstNodeForeachStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.FOREACH_STATEMENT:
            self._error(
                f"Expected foreach statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.expr, scope, expr)
        blk = []
        fescope = scope.new_child("foreach")
        fescope.new_variable("it")
        self._compile_block(statement.block, fescope, blk)
        scope.discard_child(fescope)
        instructions.append((Opcode_FOREACH, expr, blk))

    def _compile_while_statement(
        self, statement: AstNodeWhileStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.WHILE_STATEMENT:
            self._error(
                f"Expected while statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.condition, scope, expr)
        blk = []
        self._compile_block(statement.block, scope, blk)
        instructions.append((Opcode_WHILE, expr, blk))

    def _compile_switch_statement(
        self, statement: AstNodeSwitchStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.SWITCH_STATEMENT:
            self._error(
                f"Expected select statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.expr, scope, expr)

        switch = {}
        for case in statement.cases:
            csw = []
            self._compile_case_statement(case, scope, csw)
            if csw[0][1] in switch.keys():
                self._error(
                    f"Duplicate case statement {csw[0][1]} @ {statement.line}:{statement.column}"
                )
            switch[csw[0][1]] = csw[0][2]
        default = []
        if statement.default is not None:
            self._compile_block(statement.default.block, scope, default)
        instructions.append((Opcode_SWITCH, expr, switch, default))

    def _compile_case_statement(
        self, statement: AstNodeCaseStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.CASE_STATEMENT:
            self._error(
                f"Expected case statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.expr, scope, expr)
        if expr[0][0] != Opcode_LOAD_CONSTANT:
            self._error(
                f"Case expression must be a constant, got {expr[0][0]} @ {statement.line}:{statement.column}"
            )
        blk = []
        self._compile_block(statement.block, scope, blk)
        instructions.append((Opcode_CASE, expr[0][1], blk))

    def _compile_select_statement(
        self, statement: AstNodeSelectStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.SELECT_STATEMENT:
            self._error(
                f"Expected select statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        from_expr = []
        self._compile_expression(statement.From, scope, from_expr)
        where_expr = []
        if statement.Where is not None:
            self._compile_expression(statement.Where, scope, where_expr, True)
        into_expr = []
        self._compile_expression(statement.Into, scope, into_expr, True)
        instructions.append(
            (
                Opcode_SELECT,
                statement.Fields,
                from_expr,
                where_expr,
                statement.distinct,
                statement.merge,
                into_expr,
            )
        )

    def _compile_function_call_statement(
        self,
        statement: AstNodeFunctionCallStatement,
        scope: NewScope,
        instructions: list,
    ):
        if statement.expr_type != AstNodetype.FUNCTION_CALL:
            self._error(
                f"Expected function call, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        func = scope.get_function(statement.name)
        if func is None:
            self._error(
                f"Unknown function {statement.name} @ {statement.line}:{statement.column}"
            )
        args = []
        for arg in statement.args:
            self._compile_expression(arg, scope, args)
        instructions.append((Opcode_CALL, statement.name, len(statement.args), args))

    def _compile_is_type_statement(
        self, statement: AstNodeIsType, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.IS_TYPE_STATEMENT:
            self._error(
                f"Expected is type statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.expr, scope, expr)
        instructions.append((Opcode_IS_TYPE, expr, statement.TypeToCheck))

    def _compile_type_statement(
        self, statement: AstNodeTypeStatement, scope: NewScope, instructions: list
    ):
        if statement.expr_type != AstNodetype.TYPE_STATEMENT:
            self._error(
                f"Expected type statement, got {statement.expr_type} @ {statement.line}:{statement.column}"
            )
        expr = []
        self._compile_expression(statement.expr, scope, expr)
        instructions.append((Opcode_TYPE_STATEMENT, expr))

    # Include implementation

    def _find_library(self, name: str) -> Optional[str]:
        for path in SearchPath:
            lib_path = os.path.join(path, f"{name}.mcl")
            if os.path.exists(lib_path):
                return lib_path
        return None

    def _load_library(self, path: str) -> Optional[str]:
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return f.read()

    def _compile_include_statement(
        self, statement: AstNodeIncludeStatement, scope: NewScope, instructions: list
    ) -> None:
        for lib in statement.libraries:
            if lib.name in scope.libraries:
                continue
            lib_path = self._find_library(lib.name)
            if lib_path is None:
                self._error(f"Library {lib.name} not found at {lib.line}:{lib.column}")
            source = self._load_library(lib_path)
            if source is None:
                self._error(f"Library {lib.name} not found at {lib.line}:{lib.column}")

            scope.libraries.append(lib.name)
            lib_scope = scope.new_child(lib.name)
            lib_scope.is_library = True
            lex = Lexer(source)
            tokens = lex.tokenize()
            parser = Parser(tokens, lib_path)
            ast = parser.parse()
            self._compile_program(ast, lib_scope, instructions)

    # expression functions.

    def _compile_function_call_expression(
        self,
        expression: AstNodeFunctionCallExpression,
        scope: NewScope,
        instructions: list,
    ):
        if expression.expr_type != AstNodetype.FUNCTION_CALL_EXPRESSION:
            self._error(
                f"Expected function call expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        args = []
        func = scope.get_function(expression.name)
        if func is None:
            self._error(
                f"Unknown function {expression.name} @ {expression.line}:{expression.column}"
            )
        for arg in expression.args:
            self._compile_expression(arg, scope, args)
        instructions.append((Opcode_CALL, expression.name, len(expression.args), args))

    def _compile_expression(
        self,
        expression: AstNodeExpression,
        scope: NewScope,
        instructions: list,
        allow_new_variable: bool = False,
    ):
        if expression.expr_type == AstNodetype.BINARY_EXPRESSION:
            self._compile_binary_expression(
                expression, scope, instructions, allow_new_variable=allow_new_variable
            )
        elif expression.expr_type == AstNodetype.LITERAL_EXPRESSION:
            self._compile_literal_expression(expression, scope, instructions)
        elif expression.expr_type == AstNodetype.UNARY_EXPRESSION:
            self._compile_unary_expression(expression, scope, instructions)
        elif expression.expr_type == AstNodetype.VARIABLE_EXPRESSION:
            self._compile_variable_expression(
                expression, scope, instructions, allow_new_variable=allow_new_variable
            )
        elif expression.expr_type == AstNodetype.FUNCTION_CALL_EXPRESSION:
            self._compile_function_call_expression(expression, scope, instructions)
        elif expression.expr_type == AstNodetype.INDEXED_VARIABLE_EXPRESSION:
            self._compile_indexed_variable_expression(expression, scope, instructions)
        elif expression.expr_type == AstNodetype.VARIABLE_FUNCTION_CALL_EXPRESSION:
            self._compile_variable_function_call_expression(
                expression, scope, instructions
            )
        elif expression.expr_type == AstNodetype.IS_TYPE_STATEMENT:
            self._compile_is_type_statement(expression, scope, instructions)
        elif expression.expr_type == AstNodetype.TYPE_STATEMENT:
            self._compile_type_statement(expression, scope, instructions)
        else:
            self._error(
                f"Unknown expression type {expression.expr_type} @ {expression.line}:{expression.column}"
            )

    def _compile_binary_expression(
        self,
        expression: AstNodeBinaryExpression,
        scope: NewScope,
        instructions: list,
        allow_new_variable: bool = False,
    ):
        if expression.expr_type != AstNodetype.BINARY_EXPRESSION:
            self._error(
                f"Expected binary expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        lhs = []
        self._compile_expression(
            expression.left, scope, lhs, allow_new_variable=allow_new_variable
        )
        rhs = []
        self._compile_expression(
            expression.right, scope, rhs, allow_new_variable=allow_new_variable
        )
        op = expression.operator
        if op == "+=" or op == "+":
            instructions.append((Opcode_ADD, lhs, rhs))
        elif op == "-=" or op == "-":
            instructions.append((Opcode_SUB, lhs, rhs))
        elif op == "*=" or op == "*":
            instructions.append((Opcode_MUL, lhs, rhs))
        elif op == "/=" or op == "/":
            instructions.append((Opcode_DIV, lhs, rhs))
        elif op == "%=" or op == "%":
            instructions.append((Opcode_MOD, lhs, rhs))
        elif op == "^=" or op == "^":
            instructions.append((Opcode_POW, lhs, rhs))
        elif op == ">=":
            instructions.append((Opcode_GTE, lhs, rhs))
        elif op == "<=":
            instructions.append((Opcode_LTE, lhs, rhs))
        elif op == "==":
            instructions.append((Opcode_EQ, lhs, rhs))
        elif op == "!=":
            instructions.append((Opcode_NEQ, lhs, rhs))
        elif op == ">":
            instructions.append((Opcode_GT, lhs, rhs))
        elif op == "<":
            instructions.append((Opcode_LT, lhs, rhs))
        elif op == "and":
            instructions.append((Opcode_AND, lhs, rhs))
        elif op == "or":
            instructions.append((Opcode_OR, lhs, rhs))
        elif op == "xor":
            instructions.append((Opcode_XOR, lhs, rhs))
        elif op == "not":
            instructions.append((Opcode_NOT, lhs, rhs))
        elif op == "&&":
            instructions.append((Opcode_AND, lhs, rhs))
        elif op == "||":
            instructions.append((Opcode_OR, lhs, rhs))
        elif op == "^^":
            instructions.append((Opcode_XOR, lhs, rhs))
        else:
            self._error(
                f"Unknown binary operator {op} @ {expression.line}:{expression.column}"
            )

    def _compile_literal_expression(
        self, expression: AstNodeLiteralExpression, scope: NewScope, instructions: list
    ):
        if expression.expr_type != AstNodetype.LITERAL_EXPRESSION:
            self._error(
                f"Expected literal expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        instructions.append((Opcode_LOAD_CONSTANT, expression.value))

    def _compile_variable_expression(
        self,
        expression: AstNodeVariableExpression,
        scope: NewScope,
        instructions: list,
        allow_new_variable: bool = False,
    ):
        if expression.expr_type != AstNodetype.VARIABLE_EXPRESSION:
            self._error(
                f"Expected variable expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        var = scope.get_variable(expression.name)
        if var is None and allow_new_variable:
            var = scope.new_variable(expression.name)
        if var is None:
            self._error(
                f"Unknown variable {expression.name} @ {expression.line}:{expression.column}"
            )
        else:
            instructions.append((Opcode_LOAD_VARIABLE, expression.name))

    def _compile_indexed_variable_expression(
        self,
        expression: AstNodeIndexedVariableExpression,
        scope: NewScope,
        instructions: list,
    ):
        if expression.expr_type != AstNodetype.INDEXED_VARIABLE_EXPRESSION:
            self._error(
                f"Expected indexed variable expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        var = scope.get_variable(expression.name)
        if var is None:
            self._error(
                f"Unknown variable {expression.name} @ {expression.line}:{expression.column}"
            )
        var_index = []
        for index in expression.index:
            self._compile_expression(index, scope, var_index)
        instructions.append((Opcode_LOAD_VARIABLE, expression.name, var_index))

    def _compile_variable_function_call_expression(
        self,
        expression: AstNodeVariableFunctionCallExpression,
        scope: NewScope,
        instructions: list,
    ):
        print("compile_variable_function_call_expression")
        if expression.expr_type != AstNodetype.VARIABLE_FUNCTION_CALL_EXPRESSION:
            self._error(
                f"Expected variable function call expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        print(expression.name)
        for arg in expression.args:
            self._compile_expression(arg, scope, instructions)
        self._error("variable function call expression Not implemented")

    def _compile_unary_expression(
        self, expression: AstNodeUnaryExpression, scope: NewScope, instructions: list
    ):
        if self.verbose:
            print("compile_unary_expression")
        if expression.expr_type != AstNodetype.UNARY_EXPRESSION:
            self._error(
                f"Expected unary expression, got {expression.expr_type} @ {expression.line}:{expression.column}"
            )
        if self.verbose:
            print(expression.operator)
        op = expression.operator
        rhs = []
        self._compile_expression(expression.expr, scope, rhs)
        if op == "-":
            instructions.append((Opcode_SUB, rhs))
        elif op == "+":
            instructions.append((Opcode_ADD, rhs))
        elif op == "not":
            instructions.append((Opcode_NOT, rhs))
        else:
            self._error(
                f"Unknown unary operator {op} @ {expression.line}:{expression.column}"
            )
