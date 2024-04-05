#
# Product:   Macal
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      24-10-2023
#
# Copyright 2023 Westcon-Comstor
#

# This is the Macal Interpreter, it will lex, parse, compile and interpret (execute).

import os

from macal.config import SearchPath
from macal.macal_binary_file_io import BINARY_FILE_EXTENSION, SOURCE_FILE_EXTENSION, LoadBinary, SaveBinary
from macal.macal_vm import MacalVm
from keyring import get_password, set_password

rt = MacalVm()

api_key = get_password("meraki", "Stage Entertainment")


rt.SetReservedVariable('sysargv', "hostname")    
rt.SetReservedVariable('configuration', "configuration")
rt.SetReservedVariable('agent_version', "version 5.0")
rt.SetReservedVariable('org_name', "Stage Entertainment")
rt.SetReservedVariable('org_id', None)
rt.SetReservedVariable('api_key', api_key)
rt.SetReservedVariable('host_name', "Stage-Entertainment-Master")
rt.SetReservedVariable('serial_number', "serial")
code = LoadBinary("meraki_device_info.mcb")
rt.Execute(code)

search_path = [
        os.path.dirname(__file__),
        os.path.join(os.path.dirname(__file__), "lib"),
        os.path.join(os.path.dirname(__file__), "lib", "ext"),
        os.getcwd(),
        os.path.join(os.getcwd(), "lib"),
        os.path.join(os.getcwd(), "lib", "ext"),
    ]
for path in search_path:
    if path not in SearchPath:
        SearchPath.append(path)

