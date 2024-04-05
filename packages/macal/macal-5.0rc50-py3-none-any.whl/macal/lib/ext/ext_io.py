# Product:   Macal
# Author:    Marco Caspers
# Date:      16-10-2023
#
#    This library is licensed under the MIT license.
#
#    (c) 2023 Westcon-Comstor
#    (c) 2023 WestconGroup, Inc.
#    (c) 2023 WestconGroup International Limited
#    (c) 2023 WestconGroup EMEA Operations Limited
#    (c) 2023 WestconGroup European Operations Limited
#    (c) 2023 Sama Development Team
#
# IO Library external functions

import json
import os
from typing import Any


def loadTextFile(fileName: str) -> str:
    """Implementation of Load function"""
    with open(fileName, "r") as tf:
        content = tf.read()
    return content


def readJSONFile(fileName: str) -> str:
    """Implementation of Read JSON file function"""
    with open(fileName, "r") as fp:
        content = json.load(fp)
    return content


def existsFile(filename: str) -> bool:
    """Implementation of Exists function"""
    return os.path.exists(filename)


def saveTextFile(filename: str, content: str) -> bool:
    """Implementation of Save function"""
    with open(filename, "w") as tf:
        tf.write(content)
    return True


def writeJSONFile(filename: str, content: str) -> bool:
    """Implementation of Save function"""
    with open(filename, "w") as fp:
        json.dump(content, fp, indent=4)
    return True


def getLastRun(org_name: str, default: Any) -> Any:
    """Implementation of GetLastRun function"""
    fileName = f"/tmp/last_run_{org_name}.ctl"
    if os.name == "nt":
        fileName = f"c:/temp/last_run_{org_name}.ctl"
    if os.path.exists(fileName):
        with open(fileName, "r") as tf:
            result = tf.read()
        if result is None or result == "":
            result = default
    else:
        result = default
    return result


def setLastRun(org_name: str, iso_now: Any) -> Any:
    """Implementation of SetLastRun function"""
    fileName = f"/tmp/last_run_{org_name}.ctl"
    if os.name == "nt":
        fileName = f"c:/temp/last_run_{org_name}.ctl"
    with open(fileName, "w") as tf:
        tf.write(iso_now)
