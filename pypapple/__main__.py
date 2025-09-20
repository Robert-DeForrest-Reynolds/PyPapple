if __name__ != '__main__': raise ImportError("__main__ not importable")

from sys import argv
from os import path
from typing import List

from . import Interpreter

__version__:str
with open('setup.cfg') as cfg:
    __version__ = next(l.split('=')[1].strip() for l in cfg if l[:7] == "version")

print(f'(PyPapple) Pineapple {__version__}\n')

if len(argv) <= 1:
    print("Opening in REPL...")
else:
    source_path:str = argv[1]
    if not path.exists(source_path):
        print('Invalid filename provided')
    print(f'Reading {source_path}...')
    code:List[str]
    with open(source_path, 'r') as code_file:
        code = [line.strip() for line in code_file.readlines()]
    Interpreter(code=code)
