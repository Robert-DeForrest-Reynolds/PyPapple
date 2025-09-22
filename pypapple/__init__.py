'''
minimal implementation requirements:
 - the syntax in full implementation
 - the language should feel like it will when written in full using C
 - thought-through implementation of error handling
 - a LSP for vscode so the language can actually be used

what does not need to be in the language:
 - standard library implementations Python already handles (string manipulation, packing/unpacking or structuring/destructuring, etc.)
 - quality of life implementations that are not paramount to the fundamental developer workflow
 - anything not really in the tech_doc.md



'''

from typing import List
from sys import argv
from os import path, environ
from .util import *
from .interpreter import Interpreter

__version__:str


def run():
    if len(argv) <= 1: error("No source file given\n")
    if '-d' in argv: environ['dev'] = '~'
    source_path:str = next(arg for arg in argv if arg.endswith(".papple"))

    global __version__
    with open('setup.cfg') as cfg:
        __version__ = next(l.split('=')[1].strip() for l in cfg if l[:7] == "version")

    log(f'(PyPapple) Pineapple {__version__}\n')
    
    if not path.exists(source_path):  error('Invalid filename provided')
    
    log(f'Reading {source_path}...\n')
    
    code:List[str]
    with open(source_path, 'r') as code_file:
        code = code_file.readlines()
    
    Interpreter(code=code)
