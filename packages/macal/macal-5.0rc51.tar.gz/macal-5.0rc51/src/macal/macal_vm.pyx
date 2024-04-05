# cython: language_level=3
# The above lines are for cython, they are not needed for python.
# -*- coding: utf-8 -*-
#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      22-11-2023
#
# Copyright 2023 Westcon-Comstor
#

# This is the Macal Virtual Machine Interpreter, it will execute the Macal code.

import importlib
import importlib.util
import os
import sys
from typing import Any, Optional, Union, List, Dict

from .ast_nodetype import AstNodetype
from .ast_node_select_field import AstNodeSelectField
from .config import SearchPath
from .macal_conversions import typeFromValue, typeToStr, pythonTypeToStr
from .macal_opcode import *
from .macal_variable import MacalVariable
from .macal_vm_scope import NewVMScope

from .python_module_info import ModuleInfo

class ExpressionResult:
    def __init__(self, value: Any, is_variable: bool, is_indexed: bool, index: Optional[List]):
        self.value = value
        self.is_variable = is_variable
        self.is_indexed = is_indexed
        self.index = index

    def __str__(self) -> str:
        return f"ExpressionResult({self.value}, {self.is_variable}, {self.is_indexed}, {self.index})"

class MacalVm:
    def __init__(self, verbose: Optional[bool] = None, hide_output: bool = False):
        self.scope: NewVMScope = None
        self.verbose = verbose
        self.exitcode = 0
        self.LoadedModules: Dict[str, ModuleInfo] = {}
        self.ReservedVariables: List[MacalVariable] = []
        self.hide_output = hide_output
        self.scope: NewVMScope = NewVMScope("root")

    def SetReservedVariable(self, name: str, value: Any) -> None:
        var = self.scope.new_variable(name)
        if value is None and name != "none_test":
            value = AstNodetype.NIL
        if isinstance(value, list) or isinstance(value, dict):
            var.value = value.copy()
        else:
            var.value = value
        var.value_type = typeFromValue(value)
        self.ReservedVariables.append(var)

    def Execute(self, instructions: List) -> None:
        self._execute_block(instructions, self.scope)
    
    def _execute_block(self, block: List, scope: NewVMScope) -> Any:
        # a block is a List of instructions.
        # instructions are tuples, where the first element is the opcode, and the rest are the arguments.
        # we split the instruction into opcode and arguments, and execute the opcode with the arguments.
        result = None
        if scope.continuing:
            scope.continuing = False
        if scope.breaking:
            scope.breaking = False
        if scope.halting:
            return Opcode_HALT
        block_scope = scope.new_child("block")
        for instruction in block:
            op = instruction[0]
            result = self._execute_instruction(op, instruction[1:], block_scope)
            if block_scope.returning: break
            if block_scope.halting: break
            if block_scope.breaking: break
            if block_scope.continuing: break
        scope.discard_child(block_scope)
        return result

    # Expression for value always outputs a constant value.
    def _execute_expression_for_value(self, expression, scope: NewVMScope, 
                                     expand_to_string: bool = False, 
                                     iswhere:bool = False,
                                     where_item_data: Optional[Dict] = None) -> Any:
        # Note expression needs to be an array of tuples.
        result = self._execute_expression(expression = expression,
                                         scope = scope,
                                         expand_to_string = expand_to_string,
                                         iswhere = iswhere,
                                         where_item_data = where_item_data)
        if not isinstance(result, ExpressionResult):
            raise Exception(f"Expected expression result, got {pythonTypeToStr(result)}. ({scope.name})")
        output = result.value
        if result.is_variable:
            output = result.value.value
            if result.is_indexed:
                output = self._execute_walk_index(output, result.index, scope)
        if output is None:
            output = AstNodetype.NIL
        if output in [AstNodetype.BOOLEAN, AstNodetype.INTEGER, AstNodetype.FLOAT, AstNodetype.STRING,
                      AstNodetype.ARRAY, AstNodetype.RECORD, AstNodetype.NIL, AstNodetype.FUNCTION,
                      AstNodetype.PARAMS, AstNodetype.VARIABLE]:
                output = typeToStr(output)
        if expand_to_string:
            if isinstance(output, bool):
                output = "true" if output else "false"
            else:
                output = str(output)
        return output

    # Walk index of an indexable value, output is always a constant value.
    def _execute_walk_index(self, source: Any, index_to_walk: List, scope: NewVMScope) -> Any:
        if source is None:
            raise ValueError(f"Invalid input - nil. ({scope.name})")
        if not (isinstance(source, list) or isinstance(source, dict) or isinstance(source, str)):
            raise Exception(f"This variable type ({pythonTypeToStr(source)}) does not support indexing. ({scope.name})")
        if index_to_walk is None:
            raise Exception(f"Invalid index - nil. ({scope.name})")
        if len(index_to_walk) == 0:
            return source
        value = source
        for index in index_to_walk:
            if isinstance(value, dict):
                if not isinstance(index, str):
                    raise Exception(f"Invalid index type, expected string (got {pythonTypeToStr(index)}). ({scope.name})")
                if index not in value.keys():
                    raise Exception(f"Field ({index}) not found in record ({','.join(value.keys())}). ({scope.name})")
            elif isinstance(value, list) or isinstance(value, str):
                if isinstance(index, int):
                    if index < 0 or index >= len(value):
                        raise Exception(f"Array index ({index}) out of range (0-{len(value)-1}). ({scope.name})")
                else:
                    raise Exception(f"Invalid index type, expected integer (got {pythonTypeToStr(index)}). ({scope.name})")
            value = value[index]
        return value

    # Assign to index of variable
    def _assign_to_index(self, var: MacalVariable, index_to_walk: List, append: bool, value: Any, scope: NewVMScope) -> None:
        if var is None:
            raise ValueError(f"Assign - Invalid input - nil. ({scope.name})")
        if not isinstance(var, MacalVariable):
            raise Exception(f"Assign - Invalid input type, not a variable (got {pythonTypeToStr(var)}). ({scope.name})")
        if index_to_walk is None:
            raise ValueError(f"Assign ({var.name}) - Invalid index - nil. ({scope.name})")
        if not (isinstance(var.value, list) or isinstance(var.value, dict) or isinstance(var.value, str)):
            raise Exception(f"Assign ({var.name}) - Invalid value type ({pythonTypeToStr(var.value)}), index not supported. ({scope.name})")
        if len(index_to_walk) == 0:
            var.value = value
            return
        value_to_index = var.value
        if len(index_to_walk) > 1:
            for index in index_to_walk[:-1]:
                if isinstance(value_to_index, dict):
                    if not isinstance(index, str):
                        raise Exception(f"Assign ({var.name}) - Invalid index type, expected string (got {pythonTypeToStr(index)}). ({scope.name})")
                elif isinstance(value_to_index, list) or isinstance(value_to_index, str):
                    if isinstance(index, int):
                        if index < 0 or index >= len(value_to_index):
                            raise Exception(f"Assign ({var.name}) - Array index ({index}) out of range (0-{len(value)-1}). ({scope.name})")
                    else:
                        raise Exception(f"Assign ({var.name}) - Invalid index type, expected integer (got {pythonTypeToStr(index)}). ({scope.name})")
                value_to_index = value_to_index[index]
        if isinstance(value_to_index, dict):
            if not isinstance(index_to_walk[-1], str):
                raise Exception(f"Assign ({var.name}) - Invalid index type, expected string (got {pythonTypeToStr(index_to_walk[-1])}). ({scope.name})")
        if (isinstance(value_to_index, list) or isinstance(value_to_index, str)):
            if not isinstance(index_to_walk[-1], int):
                raise Exception(f"Assign ({var.name}) - Invalid index type, expected integer (got {pythonTypeToStr(index_to_walk[-1])}). ({scope.name})")
            if index_to_walk[-1] < 0 or index_to_walk[-1] >= len(value_to_index):
                raise Exception(f"Assign ({var.name}) - Array index ({index_to_walk[-1]}) out of range (0-{len(value_to_index)-1}). ({scope.name})")
        
        if append:
            if not isinstance(value_to_index[index_to_walk[-1]], list):
                raise Exception(f"Assign ({var.name}) - Invalid value type ({pythonTypeToStr(value_to_index)}), append not supported. ({scope.name})")
            v = value
            if isinstance(value, list) or isinstance(value, dict):
                v = value.copy()
            value_to_index[index_to_walk[-1]].append(v)
        else:
            value_to_index[index_to_walk[-1]] = value

    def _execute_expression(self, expression, 
                           scope: NewVMScope, 
                           expand_to_string: bool = False, 
                           allow_new_variable: bool = False,
                           iswhere: bool = False,
                           where_item_data: Optional[Dict] = None) -> ExpressionResult:
        # Note expression needs to be an array of tuples.
        op = expression[0][0]
        expr = expression[0][1:]
        if op == Opcode_LOAD_VARIABLE:
            new_var = False
            name = expr[0]
            var = scope.get_variable(name)
            index = None
            indexed = False
            if var is None and iswhere and where_item_data is not None and name in where_item_data.keys():
                return ExpressionResult(where_item_data[name], False, False, None)
            if var is None and allow_new_variable:
                var = scope.new_variable(name)
                new_var = True
            if var is None:
                raise Exception(f"Unknown variable {name}")
            if len(expr) > 1:
                if new_var is True:
                    raise Exception(f"Cannot index a new variable {name}")
                index = []
                for index_expr in expr[1]:
                    index.append(self._execute_expression_for_value([index_expr], scope, False))
                indexed = True
            return ExpressionResult(var, True, indexed, index)
        elif op == Opcode_LOAD_CONSTANT:
            v = expr[0]
            if isinstance(v, list) or isinstance(v, dict):
                v = v.copy()
            return ExpressionResult(v, False, False, None)
        elif op == Opcode_CALL:
            result = self._execute_function_call(expr, scope)
            return ExpressionResult(result, False, False, None)
        elif op == Opcode_NOT:
            lhs = self._execute_expression_for_value(expr[0], 
                                                    scope, 
                                                    iswhere= iswhere, 
                                                    where_item_data= where_item_data)
            return ExpressionResult(not lhs, False, False, None)
        elif op == Opcode_IS_TYPE:
            var = self._execute_expression(expr[0], scope)
            if var.is_variable is False:
                raise Exception("Expected variable, got constant")
            if var.value is None:
                raise Exception(f"Unknown variable {expr[0]}")
            type_to_check = expr[1]
            var_to_check: MacalVariable = var.value
            type_to_validate = typeFromValue(var_to_check.value)
            if var.is_indexed:
                type_to_validate = typeFromValue(self._execute_walk_index(var_to_check.value, var.index, scope))
            return ExpressionResult(type_to_validate == type_to_check, False, False, None)
        elif op == Opcode_TYPE_STATEMENT:
            var = self._execute_expression(expr[0], scope)
            if var.is_variable is False:
                raise Exception("Expected variable, got constant")
            if var.value is None:
                raise Exception(f"Unknown variable {expr[0]}")
            var_to_check: MacalVariable = var.value
            result = typeFromValue(var_to_check.value)
            if var.is_indexed:
                result = typeFromValue(self._execute_walk_index(var_to_check.value, var.index, scope))
            return ExpressionResult(result, False, False, None)
        elif len(expr) == 2:
            return self._execute_binary_expression(expression = expression,
                                                  scope = scope,
                                                  expand_to_string = expand_to_string,
                                                  iswhere = iswhere,
                                                  where_item_data = where_item_data)
        raise Exception(f"Unknown expression opcode {op}")
    
    def _execute_binary_expression(self, expression, scope: NewVMScope, 
                                  expand_to_string: bool = False,
                                  iswhere:bool = False,
                                  where_item_data: Optional[Dict] = None) -> ExpressionResult:
        op = expression[0][0]
        expr = expression[0][1:]
        lhs = self._execute_expression_for_value(expression = expr[0],
                                                scope = scope,
                                                expand_to_string = expand_to_string,
                                                iswhere= iswhere,
                                                where_item_data = where_item_data)
        rhs = self._execute_expression_for_value(expression = expr[1],
                                                scope = scope,
                                                expand_to_string = expand_to_string,
                                                iswhere = iswhere,
                                                where_item_data = where_item_data)
        if expand_to_string:
            lhs = str(lhs)
            rhs = str(rhs)
        if op == Opcode_ADD:
            result = lhs + rhs
        elif op == Opcode_SUB:
            result = lhs - rhs
        elif op == Opcode_MUL:
            result = lhs * rhs
        elif op == Opcode_DIV:
            result = lhs / rhs
        elif op == Opcode_MOD:
            result = lhs % rhs
        elif op == Opcode_POW:
            result = lhs ** rhs
        elif op == Opcode_GTE:
            result = lhs >= rhs
        elif op == Opcode_LTE:
            result = lhs <= rhs
        elif op == Opcode_EQ:
            result = lhs == rhs
        elif op == Opcode_NEQ:
            result = lhs != rhs
        elif op == Opcode_GT:
            result = lhs > rhs
        elif op == Opcode_LT:
            result = lhs < rhs
        elif op == Opcode_AND:
            result = lhs and rhs
        elif op == Opcode_OR:
            result = lhs or rhs
        elif op == Opcode_XOR:
            result = lhs ^ rhs
        else:
            raise Exception(f"Unknown expression opcode {op}")
        return ExpressionResult(result, False, False, None)

    def _execute_function_call(self, function: Any, scope: NewVMScope) -> Any:
        name: str = function[0]
        func_args = function[2]
        func = scope.get_function_definition(name)
        if func is None:
            raise Exception(f"Unknown function {name}")
        params = func[0]
        block  = func[1]
        module: Optional[str] = None
        ext_function: Optional[str] = None
        if func_args is None:
            raise Exception(f"Too few arguments for function {name} (expected {len(params)}, got 0).")
        if len(func_args) < len(params):
            raise Exception(f"Too few arguments for function {name} (expected {len(params)}, got {len(func_args)}).")
        if block is None:
            module: Optional[str] = func[2]
            ext_function: Optional[str] = func[3]
        args = []
        funcscope: NewVMScope = scope.new_child(name)
        funcscope.is_returnable = True
        
        for i in range(len(params)):
            param = funcscope.new_variable(params[i][1])
            arg = self._execute_expression_for_value([func_args[i]], scope)
            param.value = arg
            args.append(arg)
        if len(func_args) > len(params):
            param.value = [param.value]
            for i in range(len(params), len(func_args)):
                arg = self._execute_expression_for_value([func_args[i]], scope)
                param.value.append(arg)
                args.append(arg)
        return_value: Any = None
        if block is not None:
            return_value: Any = self._execute_block(block, funcscope)
        else:
            return_value: Any = self._run_external_function(module, ext_function, args)
        scope.discard_child(funcscope)
        return return_value

    def _execute_instruction(self, op: int, instruction, scope: NewVMScope) -> NewVMScope:
        if not scope is None and scope.halting:
            return scope
        elif op == Opcode_FUNCTION_DEFINITION:
            name = instruction[0]
            params = instruction[1]
            block = instruction[2]
            scope.function_definitions[name] = (params, block)      
        elif op == Opcode_EXTERN_FUNCTION_DEFINITION:
            name = instruction[0]
            params = instruction[1]
            module = instruction[2]
            function = instruction[3]
            scope.function_definitions[name] = (params, None, module, function)
        elif op == Opcode_NEW_VARIABLE:
            scope.new_variable(instruction[0])
        elif op == Opcode_STORE_VARIABLE:
            self._execute_assign(instruction, scope)
        elif op == Opcode_PRINT:
            prnt_scope: NewVMScope = scope.new_child("print")
            for arg in instruction[1]:
                value = self._execute_expression_for_value([arg], prnt_scope, True)
                if not self.hide_output: print(value, end="")
            scope.discard_child(prnt_scope)
            if not self.hide_output: print()
        elif op == Opcode_RET:
            scope.Return()
            if len(instruction[0]) > 0:
                retval = self._execute_expression_for_value(instruction[0], scope)
                return retval
            return None
        elif op == Opcode_HALT:
            scope.Halt()
            if len(instruction[0]) > 0:
                self.exitcode = self._execute_expression_for_value(instruction[0], scope)
        elif op == Opcode_BREAK:
            scope.Break()
        elif op == Opcode_CONTINUE:
            scope.Continue()
        elif op == Opcode_CALL:
            function_scope = scope.new_child("call")
            value = self._execute_function_call(instruction, function_scope)
            scope.discard_child(function_scope)
            return value
        elif op == Opcode_IF:
            if self._execute_expression_for_value(instruction[0], scope):
                return self._execute_block(instruction[1], scope)
            if len(instruction[2]) > 0:
                for elif_statement in instruction[2]:
                    if self._execute_expression_for_value(elif_statement[1], scope):
                        return self._execute_block(elif_statement[2], scope)
            if len(instruction[3]) > 1 and len(instruction[3][1]) > 0:
                    return self._execute_block(instruction[3][1], scope)
        elif op == Opcode_FOREACH:
            expr = self._execute_expression_for_value(instruction[0], scope)
            if not isinstance(expr, list) and not isinstance(expr, dict) and not isinstance(expr, str):
                raise Exception(f"Expected array, record or string, got {pythonTypeToStr(expr)}")
            foreach_scope: NewVMScope = scope.new_child("foreach")
            foreach_scope.is_loop = True
            it = foreach_scope.new_variable("it")
            for item in expr:
                it.value = None
                it.value = item
                if isinstance(item, dict) or isinstance(item, list):
                    it.value = item.copy()
                result = self._execute_block(instruction[1], foreach_scope)
                if foreach_scope.halting or foreach_scope.returning or foreach_scope.breaking:
                    break
                if result == Opcode_CONTINUE:
                    foreach_scope.Discontinue()
                    continue
            scope.discard_child(foreach_scope)
        elif op == Opcode_WHILE:
            while_scope: NewVMScope = scope.new_child("while")
            while_scope.is_loop = True
            while self._execute_expression_for_value(instruction[0], scope):
                result = self._execute_block(instruction[1], while_scope)
                if while_scope.breaking or while_scope.halting or while_scope.returning:
                    break
                if while_scope.continuing:
                    continue
            if while_scope.halting:
                scope.halting = True
            scope.discard_child(while_scope)
        elif op == Opcode_SWITCH:
            expr = self._execute_expression_for_value(instruction[0], scope)
            if expr in instruction[1].keys():
                return self._execute_block(instruction[1][expr], scope)
            if len(instruction[2]) > 0:
                return self._execute_block(instruction[2], scope)
        elif op == Opcode_SELECT:
            value = self._execute_select(instruction, scope)
        else:
            raise Exception("Unknown instruction: ", op, " @ ", scope.name, " ", instruction)
        return scope

    def _execute_assign(self, instruction, scope: NewVMScope):
        var_instruction    = instruction[0]
        rhs_instruction    = instruction[1]
        append = True if len(instruction) > 2 and instruction[2] else False
        # Get the variable to assign to.
        result = self._execute_expression(var_instruction, scope)
        if result.is_variable is False:
            raise Exception("Invalid type, expected variable (got constant).")
        if result.value is None:
            raise Exception(f"Variable ({var_instruction[0][1]}) not found.")
        variable_to_assign_to: MacalVariable = result.value
        # Get the value to assign.
        value_to_assign = self._execute_expression_for_value(rhs_instruction, scope)
        # check if we have an index, if so, we assign to the index.
        if result.is_indexed:
            self._assign_to_index(variable_to_assign_to, result.index, append, value_to_assign, scope)
        else: # no index, we assign to the variable.
            if append:
                variable_to_assign_to.value.append(value_to_assign)
            else:
                variable_to_assign_to.value = value_to_assign
    
    def _execute_select(self, instruction, scope: NewVMScope):
        fields: List[AstNodeSelectField] = instruction[0]
        where_expr = instruction[2]
        distinct: bool = instruction[3]
        merge: bool = instruction[4]
        destination_data: Union[List[dict], dict] = []
        
        # get the destination data if we do a merge:
        if merge is True:
            destination_data: Union[List[dict], dict] = self._execute_expression_for_value(instruction[5], scope)

        # gets the destination variable, allow creation of a new variable if we do not merge.
        into_expr_result = self._execute_expression(instruction[5], scope, allow_new_variable=not merge)
        if into_expr_result.is_variable is False:
            raise Exception("Select into expected variable, got constant")
        into_var: MacalVariable = into_expr_result.value
        if merge is False:
            if into_expr_result.is_indexed:
                self._assign_to_index(into_var, into_expr_result.index, False, None, scope)
            else:
                into_var.value = None
        
        # we get the source data by executing the from instruction.
        source_data: Union[list, dict] = self._execute_expression_for_value(instruction[1], scope)
        if source_data is None or source_data is False or source_data == AstNodetype.NIL or source_data == "nil":
            source_data: Union[List[dict], dict] = []

        # check if we have an array or record, if not, we throw an exception.
        if not isinstance(source_data, list) and not isinstance(source_data, dict):
            raise Exception(f"Invalid from data type expected array or record (got {pythonTypeToStr(source_data)}).")
        if not isinstance(destination_data, list) and not isinstance(destination_data, dict):
            raise Exception(f"Invalid destination data type, expected array, record or string (got {pythonTypeToStr(destination_data)}).")

        # convert the source data to an array if it is a record.
        if isinstance(source_data, dict):
            source_data: Union[List[dict], dict] = [source_data]

        # if we have a where expression, we filter the source data.
        
        result_data = source_data
        if len(where_expr) > 0:
            result_data = []
            where_scope = scope.new_child("where")
            for item in source_data:
                if self._execute_expression_for_value(where_expr, where_scope, iswhere=True, where_item_data=item) is False:
                    continue
                if distinct and item not in result_data:
                    result_data.append(item)
                elif not distinct:
                    result_data.append(item)
            scope.discard_child(where_scope)
        
        # source data is filtered into the result data.
        # we will now apply the field filters to the result data if we do not have a select all (*).
        if not (len(fields) == 1 and fields[0].fieldname == "*"):
            if len(result_data) == 0:
                result_data = [{field.altfieldname: AstNodetype.NIL for field in fields}]
            else:
                result_data = [{field.altfieldname: item.get(field.fieldname, AstNodetype.NIL) for field in fields} for item in result_data]
                
        # distinct always results in a single record no matter what.
        # also if there is only 1 record in the result data, we also return it as a single record.
        if isinstance(result_data, list) and distinct is True and len(result_data) > 0:
            result_data = result_data[0]

        # if we have a merge, we merge the result data into the destination data.
        if merge is True:
            destination_data: Union[List[dict], dict] = self._merge_data(destination_data, result_data).copy()
        else:
            destination_data: Union[List[dict], dict] = result_data.copy()

        # distinct always results in a single record no matter what.
        # also if there is only 1 record in the result data, we also return it as a single record.
        # there is a potential problem here if the destination data is a single record, and we have a distinct,
        if isinstance(destination_data, list) and distinct is True and len(destination_data) > 0:
            destination_data: Union[List[dict], dict] = destination_data[0]
        if distinct is True and len(destination_data) == 1:
            destination_data: Union[List[dict], dict] = destination_data[list(destination_data.keys())[0]]

        # we now have the final result data, we store it into the destination variable.
        # we need to take into account if the destination variable has an index or not.
        value = destination_data
        if isinstance(destination_data, dict) or isinstance(destination_data, list):
            value = destination_data.copy()

        if into_expr_result.is_indexed:
            self._assign_to_index(into_var, into_expr_result.index, False, value, scope)
        else:
            into_var.value = value

    def _merge_data(self, source_data: Union[List[dict], dict], destination_data: Union[List[dict], dict]) -> Any:
        if isinstance(source_data, dict):
            source_data: Union[List[dict], dict] = [source_data]
        if isinstance(destination_data, dict):
            destination_data: Union[List[dict], dict] = [destination_data]
        if not (isinstance(source_data, list) and isinstance(destination_data, list)):
            raise Exception("MERGE: Type error, both parameters must be arrays.")
        if len(source_data)== 0 and len(destination_data) == 0:
            return []
        if len(source_data) == 0 and len(destination_data) > 0:
            final_data = destination_data.copy()
        elif len(source_data) > 0 and len(destination_data) == 0:
            final_data = source_data.copy()
        elif len(source_data) == 1 and len(destination_data) == 1 and set(source_data[0].keys()) != set(destination_data[0].keys()):
            keys = set().union(source_data[0].keys(), destination_data[0].keys())
            final_data = {}
            for k in keys:
                final_data[k] = source_data[0].get(k, AstNodetype.NIL)
                v = destination_data[0].get(k, AstNodetype.NIL)
                if v != AstNodetype.NIL:
                    final_data[k] = v
            final_data = [final_data.copy()]
        # multiple records in each, with the same set of fields, then just append them both.
        elif set(source_data[0].keys()) == set(destination_data[0].keys()):
            final_data = source_data.copy()
            for rec in destination_data:
                final_data.append(rec.copy())
        # multiple records in each, but with different field sets, is an error.
        elif set(source_data[0].keys()) != set(destination_data[0].keys()):
            raise Exception(f"MERGE: Type error, data to merge must be a single records if the fields are different. ({list(source_data[0].keys())} != {list(destination_data[0].keys())})")
        if len(final_data) == 1:
            return final_data[0]
        return final_data

    def _import_module(self, module_name: str) -> Optional[Any]:
        try:
            return importlib.import_module(module_name)
        except ImportError:
            return None

    def _import_module_from_path(self, module_name: str) -> Optional[Any]:
        try:
            for path in SearchPath:
                path = os.path.join(path, f"{module_name}.py")
                if not os.path.exists(path): continue
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None: continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except ImportError as ex:
            self._Error(f"Import error: {ex}")
        return None

    def _run_external_function(self, module_name: str, function_name: str, args ) -> Any:
        module = self.LoadedModules.get(module_name, None)
        if module is None:
            imported_module = self._import_module(module_name)
            if imported_module is None:
                imported_module = self._import_module_from_path(module_name)
                if imported_module is None:
                    raise Exception(f"Module {module_name} not found.")
            module = ModuleInfo(module_name, imported_module)
            self.LoadedModules[module_name] = module
        function = module.functions.get(function_name, None)
        if function is None:
            raise Exception(f"Function {function_name} not found in module {module_name}.")
        result = function(*args)
        if result is None:
            result = AstNodetype.NIL
        return result
