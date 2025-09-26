from typing import Any
from enum import Enum
from .util import log


class P_Object:
    name:str
    value:Any
    type:type
    def __init__(_, name, value=None, type=str):
        _.name = name
        _.value = value if value else 'none'
        log(f"Instantiating Object {_.name}", important=True)

    
    @property
    def out(_) -> str: return str(_.value)