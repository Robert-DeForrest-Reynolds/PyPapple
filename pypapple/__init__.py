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
    argv.pop(0)
    if len(argv) == 0: error("No source file given\n")
    source_path:str = None
    argv_copy = argv.copy()
    for arg in argv:
        if '-log' in arg:
            log_type = arg.split('=')[1].strip()
            if log_type in ['verbose', 'v', 'log', 'l', 'critical', 'c']:
                if len(log_type) == 1:
                    log_type = {'v':'verbose', 'l':'log', 'c':'critical'}[log_type]
                environ['dev'] = log_type
                argv_copy.remove(arg)
        elif '-max_cycles' in arg:
            try:
                cycles = arg.split('=')[1].strip()
                if int(cycles) <= 0: 
                    print("-max_cycles must be more than 0")
                    exit(1)
                environ['-max_cycles'] = cycles
                argv_copy.remove(arg)
            except ValueError as e:
                print("-max_cycles must be a valid number")
                exit(0)
        elif arg.endswith('.papple'):
            source_path = arg
            argv_copy.remove(arg)

    if argv_copy:
        error(f'Unparsable argument(s): {argv_copy}')
        exit(0)

    if not source_path:
        error("No valid source path given")
        exit(0)

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
