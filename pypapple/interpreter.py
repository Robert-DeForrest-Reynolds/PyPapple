from typing import List, Callable
from os import environ
from sys import getrecursionlimit, setrecursionlimit
from .util import *
from .p_object import P_Object

from .standard import *

class Interpreter:
    code:List[str]
    original_code:List[str]
    keywords:dict[str,Callable]
    current_line_index:int
    def __init__(_, code:List[str]=None) -> None:
        _.code = []
        for line in code:
            stripped = line.strip()
            _.code.append(stripped)
        _.original_code = _.code.copy()
        _.interpreting = True
        if '-max_cycles' in environ.keys():
            cycle_count = int(environ['-max_cycles'])
            _.unbounded_cycle_count = cycle_count
            setrecursionlimit(cycle_count)
        else:
            _.unbounded_cycle_count = getrecursionlimit()
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
            "Out":lambda *args: output(_, *args)
        }
        _.namespaces = {}

        _.current_line_index:int = 0

        while _.interpreting and _.unbounded_cycle_count != 0:
            _.execute_next()
            _.unbounded_cycle_count -= 1
        


    def execute_next(_) -> None:
        try: _.code[0]
        except IndexError:
            log('End of File reached')
            _.interpreting = False
            return

        _.current_line_index += 1
        if _.code[0] == '':
            _.code = _.code[1:]
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
                error(f'Unparsable line, ignoring completely: `{potential}`',
                      line=_.current_line_index)
                _.code = _.code[1:]


    def find_closing_symbol(_, opening_symbol:str, closing_symbol) -> str:
        'Removes code from _.code where necessary'
        required_brackets:int = 0
        small_quote = False
        content:str
        big_quote = False
        for line_index, line in enumerate(_.code):
            last_symbol_index:int = 0
            line:str
            for char_index, character in enumerate(line):
                if character == "'" and not big_quote:
                    small_quote = not small_quote
                    continue
                if character == '"' and not small_quote:
                    big_quote = not big_quote
                    continue
                if not small_quote and not big_quote:
                    if character == opening_symbol: required_brackets += 1
                    if character == closing_symbol:
                        last_symbol_index:int = char_index
                        required_brackets -= 1
                        
            if required_brackets == 0:
                content = ''.join(_.code[:line_index]) + line[:last_symbol_index+1]
                leftover = line[last_symbol_index+1:]
                if leftover and not leftover.strip().startswith("~"):
                    _.code = [leftover] + _.code[line_index+1:]
                    _.current_line_index += line_index
                else:
                    _.code = _.code[line_index+1:]
                    _.current_line_index += line_index
                return content
            
        error(f"Unmatched `{opening_symbol}` (no closing `{closing_symbol}` found)",
              line=_.current_line_index)
        exit(0)


    def parse_assignment(_):
        assignment = _.code[0].strip().split('=')
        assignee_name:str = assignment[0].strip()
        assignee:P_Object
        if assignee_name in _.namespaces: assignee = _.namespaces[assignee_name]
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
        content = _.find_closing_symbol("{", "}")
        log(f'Try contents:{content}\n')


    def parse_call(_):
        content = _.find_closing_symbol("(", ")")
        para_index = content.find("(")
        caller = content[:para_index]
        arguments = content[para_index+1:-1]
        if ',' in arguments: # multiple arguments
            arguments = ...
        result = _.callables[caller](arguments)
        log(f'Call contents:{content}\n')