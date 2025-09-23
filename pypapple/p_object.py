from typing import Any
from .util import log

class P_Object:
    name:str
    value:Any
    def __init__(_, name, value = None):
        _.name = name
        _.value = value
        log(f"Instantiating Object {_.name}", important=True)