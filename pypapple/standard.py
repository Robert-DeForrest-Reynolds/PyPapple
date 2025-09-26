from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interpreter import Interpreter

from .util import *


__all__ = ['P_out', 'P_in']


def P_out(_:Interpreter, msg:str|list[str]) -> None:
    log(f"P_out args: {msg}")
    output_values:list[str] = []
    for arg in msg:
        if arg[0] in ['"', "'"]:
            formatted = ""
            open_bracket_count = arg.count('{')
            if open_bracket_count >= 1:
                if open_bracket_count == arg.count('}'):
                    actuals = []
                    split = arg.split("}")
                    for s in split:
                        actuals.extend(s.split("{"))
                    for item in actuals:
                        if item in ["'", '"']: continue
                        if item in _.current_namespace:
                            formatted += _.current_namespace[item].out
                        else:
                            formatted += item[1:]
                else:
                    error(f"mismatched formatting {arg}")
            else:
                output_values += arg[1:-1]
        else:
            value = None
            if arg in _.current_namespace:
                if _.current_namespace[arg].out:
                    value = _.current_namespace[arg].out
                else:
                    value = "None"
            # if not value:
            #     value = str(_.evaluate_expression(arg).out)
            
            if value:
                output_values.append(value)
            else:
                error(f'P_Out | Unknown value: {arg}')
                return
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