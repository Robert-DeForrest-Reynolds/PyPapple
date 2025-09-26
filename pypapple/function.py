from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interpreter import Interpreter

from typing import Any
from copy import deepcopy
from .util import *
from .p_object import P_Object

class Function():
    namespaces:dict
    reserved:dict
    return_item:Any
    # tokens[name, params:list[str], return-value, block:list[str]]
    def __init__(_, tokens:list[str|list[str]]) -> None:
        _.tokens = tokens
        _.name = tokens[0]
        _.params = tokens[1]
        _.return_item = tokens[2]
        _.block = tokens[3]

        _.namespaces = {}
        for param in _.params:
            _.namespaces.update({param:P_Object(param)})

        _.reserved = {}

        log(f'{_.name} namespace: {_.namespaces}')


    def __call__(_, pypapple:Interpreter, args):
        log(f"Calling {_.name}", important=True)
        result = pypapple.execute_function(_, args)
        return result