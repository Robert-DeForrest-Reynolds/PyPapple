from typing import List, Callable
from os import environ
from sys import getrecursionlimit, setrecursionlimit
from .util import *
from .p_object import P_Object

from .standard import *


class Function():
    signature:str
    source:str
    arguments:list[str]
    namespace:dict
    reserved:dict
    def __init__(_, signature, content:str) -> None:
        _.signature = signature
        _.source = [instruction for instruction in content if instruction != '']
        _.namespace = {}
        _.reserved = {}
        split = _.signature.split('(')
        _.name = split[0].strip().split(" ")[1]
        _.arguments = split[1].split(")")[0].split(",")
        for arg in _.arguments:
            _.namespace.update({arg:None})

        log(f'Function namespace: {_.namespace}')
        log(f'Function source: {_.source}')


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
            _.cycle_count = cycle_count
            setrecursionlimit(cycle_count)
        else:
            _.cycle_count = -1
            _.cycle_count = getrecursionlimit()
        _.reserved = {
            # separation with a space is required
            'fnc':_.parse_function,
            'obj':_.parse_object,
            'try':_.parse_try,
            'for':_.parse_for,
            'if':_.parse_if,
            'while':_.parse_while,

            # separation with a space is optional
            'out':_.parse_call,

            '=':_.parse_assignment,
        }
        _.callables = {
            "out":lambda *args: output(_, *args)
        }
        _.temp = False
        _.temp_reserved = {}
        _.temp_namespace = {}
        _.namespaces = {}

        _.current_line_index:int = 0

        if _.cycle_count == -1:
            while _.interpreting:
                _.execute_next()
        else:
            while _.interpreting and _.cycle_count != 0:
                _.execute_next()
                _.cycle_count -= 1
        

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


    def execute_function_body(_, f:Function) -> None:
        storage = _.code.copy()
        _.code = f.source
        _.temp = True
        _.temp_namespace = f.namespace
        _.temp_reserved = f.reserved
        while len(_.code) > 0:
            log(f'Parsing Block Line: {_.code[0]}', important=True)
            _.parse()
        _.code = storage
        _.temp = False
        _.temp_namespace = {}
        _.temp_reserved = {}



    def parse(_):
        # Remove comments from line
        code = _.code[0].split("~")[0].strip()
        if len(code) == 0:
            log("Ignoring comment")
            _.code = _.code[1:]
            return

        # catches all space separated reserves
        potential = code.split(" ")[0].strip()
        if potential in _.reserved or potential in _.temp_reserved:
            _.reserved[potential]()
            return

        # catch calls
        potential = code.split("(")[0].strip()
        if potential in _.reserved or potential in _.temp_reserved:
            _.reserved[potential]()
            return

        # catch assignments, do this last as it's the heaviest
        for char in code:
            if char == '=':
                _.parse_assignment()
                return
        
        
        error(f'Unparsable line: `{potential}`',
                line=_.current_line_index)
        exit(0)


    def find_closing_symbol(_, opening_symbol:str, closing_symbol) -> list[str, list[str]]:
        'Removes code from _.code where necessary'
        required_brackets:int = 0
        content:str
        small_quote = False
        big_quote = False
        first_bracket = False
        signature = ""
        open_line_index = 0
        open_char_index = 0
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
                    if character == opening_symbol:
                        if first_bracket == False:
                            signature = line[:char_index].strip()
                            open_line_index = line_index
                            open_char_index = char_index
                            first_bracket = True
                        required_brackets += 1
                    if character == closing_symbol:
                        last_symbol_index:int = char_index
                        required_brackets -= 1
                        
            if required_brackets == 0:
                content:list = []
                if open_line_index == line_index:
                    content.append(_.code[open_line_index][open_char_index+1:-1])
                else:
                    if _.code[open_line_index][open_char_index+1:] != '':
                        content.append(_.code[open_line_index][open_char_index+1:])
                    
                    content.extend(_.code[open_line_index+1:line_index])
                    
                    if _.code[line_index][0].strip() != closing_symbol:
                        content.append(_.code[line_index][:char_index])
                leftover = line[last_symbol_index+1:]
                if leftover and not leftover.strip().startswith("~"):
                    _.code = [leftover] + _.code[line_index+1:]
                    _.current_line_index += line_index
                else:
                    _.code = _.code[line_index+1:]
                    _.current_line_index += line_index
                return signature, content
            
        error(f"Unmatched `{opening_symbol}` (no closing `{closing_symbol}` found)",
              line=_.current_line_index)
        exit(0)


    def parse_assignment(_):
        assignment = _.code[0].strip().split('=')
        assignee_name:str = assignment[0].strip()
        assignee:P_Object
        if _.temp:
            if assignee_name in _.temp_namespace: assignee = _.temp_namespace[assignee_name]
            else:
                _.temp_namespace.update({assignee_name:P_Object(assignee_name)})
                assignee = _.temp_namespace[assignee_name]
            assignment_str = assignment[1].strip()
            if assignment_str in _.temp_namespace:
                assignee.value = _.temp_namespace[assignment_str]
        else:
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
        signature, content = _.find_closing_symbol("{", "}")
        f = Function(signature, content)
        _.reserved.update({f.name:_.parse_call})
        _.namespaces.update({f.name:f})
        log(f'Function signature: {signature}\n')
        log(f'Function contents: {content}\n')


    def parse_object(_):
        signature, content = _.find_closing_symbol("{", "}")
        log(f'Object signature: {signature}\n')
        log(f'Object contents: {content}\n')


    def parse_try(_):
        signature, content = _.find_closing_symbol("{", "}")
        log(f'Try contents: {content}\n')


    def parse_for(_):
        signature, content = _.find_closing_symbol("{", "}")
        log(f'For signature: {signature}\n')
        log(f'For contents: {content}\n')


    def parse_while(_):
        signature, content = _.find_closing_symbol("{", "}")
        log(f'While signature: {signature}\n')
        log(f'While contents: {content}\n')


    def parse_if(_):
        signature, content = _.find_closing_symbol("{", "}")
        log(f'If signature: {signature}\n')
        log(f'If contents: {content}\n')


    def parse_call(_):
        signature, content = _.find_closing_symbol("(", ")")
        log(f'Call signature: {signature}\n')
        log(f'Call contents:{content}\n')
        passed_arguments = content[0].split(",")
        if signature in _.namespaces:
            f:Function = _.namespaces[signature]
            for index, arg in enumerate(passed_arguments):
                f.namespace[f.arguments[index]] = arg
            result = _.execute_function_body(f)
        elif signature in _.callables:
            result = _.callables[signature](content)