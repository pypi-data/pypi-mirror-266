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


rt = MacalVm()
print("Hostname: ", "hostname")
print("API Key: ", "apikey")
print("Orgid: ", "orgiid")
print("Orgname: ", "hostname")
print("Script: ", "script")
print("Device serial: ", "serial")    
        
rt.SetReservedVariable('sysargv', "hostname")    
rt.SetReservedVariable('configuration', "configuration")
rt.SetReservedVariable('agent_version', "version 5.0")
rt.SetReservedVariable('org_name', "orgname")
rt.SetReservedVariable('org_id', "orgid")
rt.SetReservedVariable('api_key', "apikey")
rt.SetReservedVariable('host_name', "hostname")
rt.SetReservedVariable('serial_number', "serial")
code = LoadBinary("usereserved.mcb")
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

