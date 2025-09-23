from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter

from .util import error

__all__ = ['output']

def output(_:Interpreter, msg:str|list[str]) -> None:
    output_string = ""
    for potential_str in msg:
        if potential_str[0] in ['"', "'"]:
            output_string += potential_str[1:-1]
    if len(msg) == 1:
        msg = msg[0]

    if _.temp:
        msg = _.temp_namespace[msg].value
    elif msg not in _.namespaces:
        error(f'Unknown value: {msg}')
        return

    print(msg)