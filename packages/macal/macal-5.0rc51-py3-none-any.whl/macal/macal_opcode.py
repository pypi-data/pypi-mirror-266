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

# These are the Opcode definitions for the Macal VM
# They are used to define the instruction set for the VM


Opcode_NEW_VARIABLE = 0
Opcode_NEW_SCOPE = 1
Opcode_LOAD_CONSTANT = 2
Opcode_STORE_VARIABLE = 3
Opcode_LOAD_VARIABLE = 4
Opcode_LEAVE_SCOPE = 5
Opcode_LOAD_LIBRARY = 6
Opcode_ADD = 7
Opcode_SUB = 8
Opcode_MUL = 9 
Opcode_DIV = 10
Opcode_MOD = 11
Opcode_POW = 12
Opcode_GTE = 13
Opcode_LTE = 14
Opcode_EQ = 15
Opcode_NEQ = 16
Opcode_GT = 17
Opcode_LT = 18
Opcode_AND = 19
Opcode_OR = 20
Opcode_XOR = 21
Opcode_NOT = 22
Opcode_CALL = 23
Opcode_RET = 24
Opcode_FUNCTION_DEFINITION = 25
Opcode_EXTERN_FUNCTION_DEFINITION = 26
Opcode_HALT = 27
Opcode_PRINT = 28
Opcode_CONTINUE = 29
Opcode_BREAK = 30
Opcode_FOREACH = 31
Opcode_WHILE = 32
Opcode_IF = 33
Opcode_ELIF = 34
Opcode_ELSE = 35
Opcode_SELECT = 36
Opcode_DISTINCT = 37
Opcode_FROM = 38
Opcode_WHERE = 39
Opcode_MERGE = 40
Opcode_INTO = 41
Opcode_SWITCH = 42
Opcode_CASE = 43
Opcode_DEFAULT = 44
Opcode_INDEX = 45
Opcode_IS_TYPE = 46
Opcode_TYPE_STATEMENT = 47

opcode_translation_table = {
    Opcode_NEW_VARIABLE : "NEW_VARIABLE",
    Opcode_NEW_SCOPE : "NEW_SCOPE",
    Opcode_LOAD_CONSTANT : "LOAD_CONSTANT",
    Opcode_STORE_VARIABLE : "STORE_VARIABLE",
    Opcode_LOAD_VARIABLE : "LOAD_VARIABLE",
    Opcode_LEAVE_SCOPE : "LEAVE_SCOPE",
    Opcode_LOAD_LIBRARY : "LOAD_LIBRARY",
    Opcode_ADD : "ADD",
    Opcode_SUB : "SUB",
    Opcode_MUL : "MUL",
    Opcode_DIV : "DIV",
    Opcode_MOD : "MOD",
    Opcode_POW : "POW",   
    Opcode_GTE : "GTE",
    Opcode_LTE : "LTE",
    Opcode_EQ : "EQ",
    Opcode_NEQ : "NEQ",
    Opcode_GT : "GT",
    Opcode_LT : "LT",
    Opcode_AND : "AND",
    Opcode_OR : "OR",
    Opcode_XOR : "XOR",
    Opcode_NOT : "NOT",
    Opcode_CALL : "CALL",
    Opcode_RET : "RET",
    Opcode_FUNCTION_DEFINITION : "FUNCTION_DEFINITION",
    Opcode_EXTERN_FUNCTION_DEFINITION : "EXTERN_FUNCTION_DEFINITION",
    Opcode_HALT : "HALT",
    Opcode_PRINT : "PRINT",
    Opcode_CONTINUE : "CONTINUE",
    Opcode_BREAK : "BREAK",
    Opcode_FOREACH : "FOREACH",
    Opcode_WHILE :  "WHILE",
    Opcode_IF : "IF",
    Opcode_ELIF : "ELIF",
    Opcode_ELSE : "ELSE",
    Opcode_SELECT : "SELECT",
    Opcode_DISTINCT : "DISTINCT",
    Opcode_FROM : "FROM",
    Opcode_WHERE :  "WHERE",
    Opcode_MERGE : "MERGE",
    Opcode_INTO : "INTO",
    Opcode_SWITCH : "SWITCH",
    Opcode_CASE : "CASE",
    Opcode_DEFAULT : "DEFAULT",
    Opcode_INDEX : "INDEX",
    Opcode_IS_TYPE : "IS_TYPE",
    Opcode_TYPE_STATEMENT : "TYPE_STATEMENT",
}