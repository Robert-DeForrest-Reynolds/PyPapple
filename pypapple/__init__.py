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

from typing import List, Callable, Any
from sys import argv
from os import path, environ

from .util import *
from .p_object import P_Object


__version__:str


def run():
    with open('setup.cfg') as cfg:
        __version__ = next(l.split('=')[1].strip() for l in cfg if l[:7] == "version")

    log(f'(PyPapple) Pineapple {__version__}\n')
    
    if len(argv) <= 1:
        error("No source file given\n")
    else:
        source_path:str = argv[1]
        if not path.exists(source_path):
            error('Invalid filename provided')
        log(f'Reading {source_path}...\n')
        
        code:List[str]
        with open(source_path, 'r') as code_file:
            code = code_file.readlines()
        
        if len(argv) == 3:
            if argv[2] == '-d':
                environ['dev'] = '~'
        
        Interpreter(code=code)


class Interpreter:
    code:List[str]
    original_code:List[str]
    keywords:dict[str,Callable]
    def __init__(_, code:List[str]=None) -> None:
        _.code = []
        for line in code:
            stripped = line.strip()
            _.code.append(stripped) if stripped != '' else None
        _.original_code = _.code.copy()
        _.interpreting = True
        _.unbounded_cycle_count = 32
        _.reserved = {
            '=':_.parse_assignment,
            'fnc':_.parse_function,
            'obj':_.parse_object,
            'try':_.parse_try,
            'Out':_.parse_call,
        }
        _.callables = {
            "Out":lambda *args: _.output(*args)
        }
        _.namespaces = {}

        while _.interpreting and _.unbounded_cycle_count != 0:
            _.execute_next()
            _.unbounded_cycle_count -= 1


    def execute_next(_) -> None:
        try: line = _.code[0]
        except IndexError:
            log('End of File reached')
            _.interpreting = False
            return
        
        if len(line) != 0:
            log(f'Parsing Line: {line}', important=True)
            _.parse(line)
        else: _.code.pop(0)


    def _try(_, function:Callable, optional_msg:str=None) -> bool:
        '''
        Try to execute the callable, and ignores any errors.\n
        If function call produces a callable, it will call it; non-resursive.\n
        Return True if function is executed, returns False elsewise.
        '''
        try:
            result = function()
            try:
                if callable(result):
                    result()
            except Exception as e:
                error(f'Error calling result in _try: {e}')
            return True
        except Exception as e:
            if optional_msg:
                log(optional_msg)
                log(e)
            return False


    def parse(_, line:str):
        for count, character in enumerate(line):
            potential_keyword = line[:count+1]
            if character == '~':
                if line[:count].strip() != "":
                    potential_keyword = line[:count].strip()
                    if _._try(lambda: _.reserved[line[:count].strip()]):
                        return
                    else:
                        error_line:int = _.original_code.index(line)
                        error(f'Unknown keyword: `{potential_keyword.strip()}`', line=error_line)
                # this needs to handle lines where the code comes before the comment
                _.code = _.code[1:]
                return
            
            if _._try(lambda: _.reserved[potential_keyword]):
                return

            if _._try(lambda: _.reserved[character]):
                return
        
        error_line:int = _.original_code.index(line)
        error(f'Unparsable line, ignoring completely: `{potential_keyword}`', line=error_line)
        _.code = _.code[1:]


    def find_closing_symbol(_, opening_symbol:str, closing_symbol) -> str:
        'Removes code from _.code where necessary'
        # track if there's inner brace syntax
        required_brackets:int = 0
        for count, line in enumerate(_.code):
            if opening_symbol in line and closing_symbol not in line:
                required_brackets += 1
            if closing_symbol in line:
                required_brackets -= 1
                if required_brackets <= 0:
                    content = ''.join(_.code[:count+1])
                    _.code = _.code[count+1:]
                    return content


    def parse_assignment(_):
        assignment = _.code[0].strip().split('=')
        log(f'Assignment contents:{assignment}\n')
        assignee_name:str = assignment[0].strip()
        assignee:P_Object
        if _._try(lambda: _.namespaces[assignee_name]):
            assignee = _.namespaces[assignee_name]
        else:
            _.namespaces.update({assignee_name:P_Object(assignee_name)})
            assignee = _.namespaces[assignee_name]
        assignment_str = assignment[1].strip()
        # needs to check if operation, call, or instantiation
        assignee.value = assignment_str
        log(f'Assignment Object: {assignee}')
        _.code = _.code[1:]


    def parse_function(_):
        content = _.find_closing_symbol("{", "}")
        log(f'Function contents:{content}\n')


    def parse_object(_):
        content = _.find_closing_symbol("{", "}")
        log(f'Object contents:{content}\n')


    def parse_try(_):
        ...


    def parse_call(_):
        content = _.find_closing_symbol("(", ")")
        para_index = content.find("(")
        caller = content[:para_index]
        arguments = content[para_index+1:-1]
        if ',' in arguments: # multiple arguments
            arguments = ...
        result = _.callables[caller](arguments)
        log(f'Call contents:{content}\n')


    def output(_, msg:str) -> None:
        if msg[0] in ['"', "'"]:
            msg = msg[1:-1]
        else:
            if not _._try(lambda: _.namespaces[msg]):
                error(f'Unknown value: {msg}')
                return
            msg = _.namespaces[msg].value
        print(msg)