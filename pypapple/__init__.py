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
            # separation with a space is required
            'fnc':_.parse_function,
            'obj':_.parse_object,
            'try':_.parse_try,
            'for':...,
            'if':...,
            'while':...,

            # separation with a space is optional
            'Out':_.parse_call,

            '=':_.parse_assignment,
        }
        _.callables = {
            "Out":lambda *args: _.output(*args)
        }
        _.namespaces = {}

        while _.interpreting and _.unbounded_cycle_count != 0:
            _.execute_next()
            _.unbounded_cycle_count -= 1


    def execute_next(_) -> None:
        try: _.code[0]
        except IndexError:
            log('End of File reached')
            _.interpreting = False
            return
        
        log(f'Parsing Line: {_.code[0]}', important=True)
        _.parse()


    def parse(_):
        '''
        all reserved keywords are considered 'statement headers',
        they are essentially ways to begin declaring some kind of
        statement; they signify the `statement type`

        the rest of a statement is considered `statement instructions`
        they are the actions of a statement
        
        here are the known rules so far:
        - spacing, and newlines are separators.

        types of statement headers:
        - assignment
        - call
        - class creation
        - try statement
        - if statement
        - while loop
        - for loop
        '''
        # Remove comments from line
        _.code[0] = _.code[0].split("~")[0].strip()
        if len(_.code[0]) == 0:
            log("Ignoring comment")
            _.code = _.code[1:]
            return

        # catches all space separated reserves
        potential = _.code[0].split(" ")[0]
        if potential in _.reserved:
            _.reserved[potential]()
            return
        
        # catch calls
        potential = _.code[0].split("(")[0].strip()
        if potential in _.reserved:
            _.reserved[potential]()
            return
        
        # catch assignments, do this last as it's the heaviest
        potential = _.code[0].split("=")
        if len(potential) > 1:
            try:
                _.parse_assignment()
            except:
                error_line:int = _.original_code.index(_.code[0])
                error(f'Unparsable line, ignoring completely: `{potential}`', line=error_line)
                _.code = _.code[1:]


    def find_closing_symbol(_, opening_symbol:str, closing_symbol) -> str:
        'Removes code from _.code where necessary'
        required_brackets:int = 0
        small_quote = False
        big_quote = False
        for count, line in enumerate(_.code):
            for character in line:
                if character == "'" and not big_quote:
                    small_quote = not small_quote
                    continue
                if character == '"' and not small_quote:
                    big_quote = not big_quote
                    continue
                if not small_quote and not big_quote:
                    if character == opening_symbol:
                        required_brackets += 1
                    if character == closing_symbol:
                        required_brackets -= 1
            if required_brackets <= 0:
                content = ''.join(_.code[:count+1])
                _.code = _.code[count+1:]
                return content


    def parse_assignment(_):
        assignment = _.code[0].strip().split('=')
        assignee_name:str = assignment[0].strip()
        assignee:P_Object
        if assignee_name in _.namespaces:
            assignee = _.namespaces[assignee_name]
        else:
            _.namespaces.update({assignee_name:P_Object(assignee_name)})
            assignee = _.namespaces[assignee_name]
        assignment_str = assignment[1].strip()
        if assignment_str in _.namespaces:
            assignee.value = _.namespaces[assignment_str]
        # needs to check if operation, call, or instantiation
        assignee.value = assignment_str
        log(f'Assignment contents: name=`{assignee_name}`, value=`{assignee.value}`\n')
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
        if msg[0] in ['"', "'"]: msg = msg[1:-1]
        else:
            if msg not in _.namespaces:
                error(f'Unknown value: {msg}')
                return
            msg = _.namespaces[msg].value
        print(msg)