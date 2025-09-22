from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter

from .util import error

__all__ = ['output']

def output(_:Interpreter, msg:str) -> None:
    if msg[0] in ['"', "'"]: msg = msg[1:-1]
    else:
        if msg not in _.namespaces:
            error(f'Unknown value: {msg}')
            return
        msg = _.namespaces[msg].value
    print(msg)