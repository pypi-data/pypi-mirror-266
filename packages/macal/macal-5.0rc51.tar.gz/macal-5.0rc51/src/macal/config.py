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

# Configuration module

import os
from typing import List

SearchPath: List[str] = [
    os.path.dirname(__file__),
    os.path.join(os.path.dirname(__file__), "lib"),
    os.path.join(os.path.dirname(__file__), "lib", "ext"),
]
