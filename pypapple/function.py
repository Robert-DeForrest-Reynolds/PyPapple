from typing import Any
from copy import deepcopy
from .util import *

class Function():
    signature:str
    source:str
    arguments:list[str]
    namespaces:dict
    reserved:dict
    return_item:Any
    def __init__(_, signature, content:str) -> None:
        _.signature = signature
        _.content = content
        _.source = [instruction for instruction in content if instruction != '']
        _.namespaces = {}
        _.reserved = {}
        
        split = _.signature.split('(')
        _.name = split[0].strip().split(" ")[1]
        split = split[1].split(")")

        _.arguments = [a.strip() for a in split[0].split(",") if a.strip()]

        _.return_item = split[1].strip() if split[1].strip() != '' else None

        for arg in _.arguments:
            _.namespaces.update({arg:None})

        log(f'Function namespace: {_.namespaces}')
        log(f'Function source: {_.source}')


    def __call__(_):
        log(f"Getting deep copy of {_.name}", important=True)
        return deepcopy(_)