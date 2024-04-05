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


# This is a wrapper of a python module for the library system.

from __future__ import annotations

from typing import Any


class ModuleInfo:
    def __init__(self, name: str, module: Any) -> ModuleInfo:
        self.name = name
        self.module = module
        import inspect

        members = inspect.getmembers(module)
        object_dict = {name: obj for name, obj in members}
        self.functions = {name: obj for name, obj in object_dict.items() if inspect.isfunction(obj)}

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return self.__str__()
