from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter

from .util import *


__all__ = ['P_out', 'P_in']


def P_out(_:Interpreter, msg:str|list[str]) -> None:
    log(f"P_out args: {msg}")
    output_values:list[str] = []
    for arg in msg:
        if arg[0] in ['"', "'"]:
            output_values += [arg[1:-1]]
        else:
            if arg not in _.current_namespace:
                error(f'Unknown value: {msg}')
                return
            else:
                if _.current_namespace[arg].value:
                    output_values.append(_.current_namespace[arg].value)
                else:
                    output_values.append("None")
    if len(msg) == 1:
        msg = msg[0]

    output_string = "".join(output_values)
    print(output_string)


def P_in(_:Interpreter, prefix:str|list[str]="") -> str:
    actual = prefix.pop(0)
    if actual == []:
        return 
    if prefix == ['']:
        error("in only takes 1 argument")
        return None
    if actual[0] in ['"', "'"]:
        actual = actual[1:-1]
    return input(actual)