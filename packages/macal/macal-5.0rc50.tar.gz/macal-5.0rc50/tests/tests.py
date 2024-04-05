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
# tests all mcl files in the tests directory

import os
import sys
import subprocess
from keyring import get_password
from macal.config import SearchPath
from macal.macal_binary_file_io import BINARY_FILE_EXTENSION, SOURCE_FILE_EXTENSION, LoadBinary

import pyximport; pyximport.install()
from macal.macal_vm import MacalVm

def setSearchPath():
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

def execute(code, hide_output: bool):
    api_key = get_password("meraki", "Stage Entertainment")
    rt = MacalVm(hide_output=hide_output)
    rt.SetReservedVariable('sysargv', "hostname")    
    rt.SetReservedVariable('configuration', "configuration")
    rt.SetReservedVariable('agent_version', "version 5.0")
    rt.SetReservedVariable('org_name', "Stage Entertainment")
    rt.SetReservedVariable('org_id', None)
    rt.SetReservedVariable('api_key', api_key)
    rt.SetReservedVariable('host_name', "Stage-Entertainment-Master")
    rt.SetReservedVariable('serial_number', "serial")
    rt.SetReservedVariable('script', "script")
    rt.SetReservedVariable('none_test', None)
    rt.Execute(code)
    return rt.exitcode

def main():
    # get all files in the tests directory
    file_list = os.listdir('.')

    # remove non-mcl files
    source_files = [test for test in file_list if test.endswith(SOURCE_FILE_EXTENSION)]
    # sort the tests
    source_files.sort()

    # run each test
    print('Compiling tests: ')
    print("(var_not_found_test.mcl is expected to fail!)")
    good = 0
    errors = 0
    for test in source_files:
        if test in ['test4.mcl','function.mcl','function6.mcl']:
            continue
        # get the test name
        test_name = test[:-4]
        # run the test
        p = subprocess.run(['mc', test, '-r', 'sysargv,configuration,agent_version,org_name,org_id,api_key,host_name,serial_number,script,none_test'],capture_output=True)
        if p.returncode != 0:
            print(f'Error compiling {test_name}:')
            print(p.stderr.decode('utf-8'))
            errors += 1
        else:
            good += 1
    print(f'Good: {good} Errors: {errors}, Total: {good+errors}')
    
    file_list = os.listdir('.')
    executables = [test for test in file_list if test.endswith(BINARY_FILE_EXTENSION)]
    executables.sort()
    
    print()
    print('Executing tests: ')
    print()
    good = 0
    errors = 0
    errors_list = []
    halt_count = 0
    halted = []
    for test in executables:
        test_name = test[:-4]
        code = LoadBinary(test)
        try:
            ret = execute(code, test_name != 'none_test')
            if ret != 0:
                halted.append((test_name, ret))
                halt_count += 1
            good += 1
        except Exception as e:
            errors_list.append((test_name, e))
            errors += 1
    
    print()
    print(f'Good: {good} Errors: {errors}, halted: {halt_count}, Total: {good+errors}')
    print()

    for error in errors_list:
        print(f'Error executing {error[0]}:')
        print(error[1])

    print()
    print('Tests that exit with halt:')
    print("('halt_test' and 'null' are supposed to halt with an exitcode of 3 and 42 respectively)")
    print()
    for test in halted:
        print(f"Test: '{test[0]}', exitcode: {test[1]}")


if __name__ == '__main__':
    main()