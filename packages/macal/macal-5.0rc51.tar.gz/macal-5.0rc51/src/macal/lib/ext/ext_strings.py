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
# String functions library

from typing import Any

from unidecode import unidecode


def StrLen(arg: str) -> int:
    """Implementation of len function"""
    return len(arg)


def StrLeft(arg: str, length: int) -> str:
    """Implementation of left function"""
    return arg[0:length]


def StrMid(arg: str, offset: int, length: int) -> str:
    """Implementation of mid function"""
    return arg[offset : (offset + length)]


def ToString(arg: Any) -> str:
    """Implementation of toString function"""
    if arg is True:
        return "true"
    elif arg is False:
        return "false"
    elif arg is None or arg == "NIL":
        return "nil"
    elif isinstance(arg, dict):
        vd = {k: "nil" if v is None or v == "NIL" else str(v).lower() if isinstance(v, bool) else v for k, v in arg.items()}
        return f"{vd}"
    elif isinstance(arg, list):
        vl = ["nil" if v is None or v == "NIL" else str(v).lower() if isinstance(v, bool) else v for v in arg]
        return f"{vl}"
    return str(arg)


def StrContains(needle: str, haystack: str) -> bool:
    """Implementation of strContains function"""
    if needle is None or haystack is None:
        return False
    return needle in haystack


def StrReplace(var: str, frm: str, wth: str) -> str:
    """Implementation of strReplace function"""
    if var is None:
        return None
    return var.replace(frm, wth)


def StartsWith(haystack: str, needle: str) -> bool:
    """Implementation of StartsWith function"""
    if haystack is None:
        return False
    return haystack.startswith(needle)


def RemoveNonAscii(text: str) -> str:
    """Implementation of RemoveNonAscii function"""
    if text is None:
        return None
    return unidecode(text)


def ReplaceEx(var: str, repl: Any, by: str) -> str:
    """Implementation of ReplaceEx function"""
    result = var
    if result is not None:
        for ch in repl:
            result = result.replace(ch, by)
    return result


def PadLeft(string: str, char: str, amount: int) -> Any:
    """Implementation of PadLeft function"""
    # this is counter intuitive, but the *just functions in python pad the character on the other
    # end as what their name would imply.
    if string is None:
        string = ""
    if char is None:
        char = " "
    if amount is None:
        amount = 0
    return string.rjust(amount, char)


def PadRight(string: str, char: str, amount: int) -> Any:
    """Implementation of PadRight function"""
    # this is counter intuitive, but the *just functions in python pad the character on the other
    # end as what their name would imply.
    if string is None:
        string = ""
    if char is None:
        char = " "
    if amount is None:
        amount = 0
    return string.ljust(amount, char)


def PadCenter(string: str, char: str, amount: int) -> Any:
    """Implementation of PadCenter function"""
    if string is None:
        string = ""
    if char is None:
        char = " "
    if amount is None:
        amount = 0
    return string.center(amount, char)


def StrToInt(str) -> None:
    """Convert String to Integer"""
    global LastErrorMessage
    try:
        return int(str)
    except Exception as ex:
        LastErrorMessage = f"StrToInt(): {ex}"
