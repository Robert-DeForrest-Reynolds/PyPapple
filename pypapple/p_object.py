from typing import Any
from .util import log

class P_Object:
    name:str
    value:Any
    def __init__(_, name):
        log("Instantiating Object")
        _.name = name
        _.value = None