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

# Scope for the Macal VM

from __future__ import annotations
from typing import Optional
from .macal_variable import MacalVariable


class NewVMScope:
    def __init__(self, name: str) -> NewVMScope:
        self.name = name
        self.parent: NewVMScope = None
        self.children: list[NewVMScope] = []
        self.variables: list[MacalVariable] = []
        self.function_definitions = {}
        self.is_function: bool = False
        self.is_extern: bool = False
        self.module: str = None
        self.function: str = None
        self.root: NewVMScope = self
        self.breaking: bool = False
        self.continuing: bool = False
        self.halting: bool = False
        self.returning: bool = False
        self.is_loop: bool = False
        self.is_returnable: bool = False
        
    def Halt(self):
        self.halting = True
        if self.parent is not None:
            self.parent.Halt()

    def Break(self):
        self.breaking = True
        if self.parent is not None and self.parent.is_loop:
            self.parent.Break()

    def Continue(self):
        self.continuing = True
        if self.parent is not None and self.parent.is_loop:
            self.parent.Continue()

    def Discontinue(self):
        self.continuing = False
        if self.parent is not None and self.parent.is_loop:
            self.parent.Discontinue()
        for child in self.children:
            child.Discontinue()

    def Return(self):
        self.returning = True
        if self.parent is not None and self.parent.is_returnable:
            self.parent.Return()

    def print(self, indent: int = 0):
        print(" " * indent, "Name:       ", self.name)
        print(" " * indent, "Variables:  ", len(self.variables))
        print(" " * indent, "Functions:  ", len(self.function_definitions))
        print(" " * indent, "IsFunction: ", self.is_function)
        print(" " * indent, "IsExtern:   ", self.is_extern)
        print(" " * indent, "Module:     ", self.module)
        print(" " * indent, "Function:   ", self.function)
        print(" " * indent, "Breaking:   ", self.breaking)
        print(" " * indent, "Continuing: ", self.continuing)
        print(" " * indent, "Halting:    ", self.halting)
        print(" " * indent, "Returning:  ", self.returning)
        for child in self.children:
            child.print(indent + 1)

    def add_child(self, child: NewVMScope):
        self.children.append(child)
        child.parent = self
        child.root = self.root
        child.is_loop = self.is_loop
        child.is_returnable = self.is_returnable

    def new_child(self, name: str) -> NewVMScope:
        child = NewVMScope(name)
        self.add_child(child)
        return child
    
    def get_child(self, name: str) -> NewVMScope:
        return next((child for child in self.children if child.name == name), None)
    
    def discard_child(self, child: NewVMScope):
        self.children.remove(child)
        child = None

    def __str__(self) -> str:
        return f"{self.name}({self.parent.name if self.parent is not None else None})"
    
    def get_variable(self, name: str) -> Optional[MacalVariable]:
        var = next((var for var in self.variables if var.name == name), None)
        if var is not None:
            return var
        if self.is_function:
            return var
        if self.parent is not None:
            return self.parent.get_variable(name)
        return None
    
    def get_function_definition(self, name: str):
        func = next((func for fname, func in self.function_definitions.items() if fname == name), None)
        if func is not None:
            return func
        if self.parent is not None and self.parent.name is self.name:
            if self.root is not self:
                return self.root.get_function_definition_from_root_up(name)
            return None
        if self.parent is not None:
            return self.parent.get_function_definition(name)
        return None
    
    def get_function_definition_from_root_up(self, name: str):
        func = next((func for fname, func in self.function_definitions.items() if fname == name), None)
        if func is not None:
            return func
        for child in self.children:
            func = child.get_function_definition_from_root_up(name)
            if func is not None:
                return func
        return None
    
    def new_variable(self, name: str) -> MacalVariable:
        var = MacalVariable(name, self)
        self.variables.append(var)
        return var
