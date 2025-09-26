from typing import Callable, Any
from os import environ
from sys import setrecursionlimit, getrecursionlimit

from .util import *
from .standard import *
from .p_object import P_Object
from .function import Function


class Interpreter:
    code:list[str]
    original_code:list[str]
    keywords:dict[str,Callable]
    current_line_index:int
    def __init__(_, code:list[str]=None) -> None:
        _.code = code
        print(_.code)

        _.original_code = _.code.copy()
        _.interpreting = True

        if '-max_cycles' in environ.keys():
            cycle_count = int(environ['-max_cycles'])
            _.cycle_count = cycle_count
            setrecursionlimit(cycle_count)
        else:
            _.cycle_count = -1
            _.cycle_count = getrecursionlimit()

        _.namespaces = {}
        _.reserved = {
            # separation with a space is required
            'fnc':_.parse_function,
            'obj':lambda: info("obj decl found"),
            'try':lambda: info("try found"),
            'for':lambda: info("for found"),
            'if':lambda: info("if found"),
            'while':lambda: info("while found"),

            # separation with a space is optional
            'out':lambda: info("Out function found"),
            'in':lambda: info("in function found"),
        }

        _.callables = {
            "out":lambda *args: P_out(_, *args),
            "in":lambda *args: P_in(_, *args),
        }

        _.temp = False
        _.temp_function_signature = 'fnc __temp__()'
        _.temp_reserved:dict[str:Callable|P_Object|Function] = {}
        _.temp_namespaces:dict[str:P_Object|Function] = {}

        _.return_item = None

        _.current_line_index:int = 0

        if _.cycle_count == -1:
            while _.interpreting:
                _.execute_next_line()
        else:
            while _.interpreting and _.cycle_count != 0:
                _.execute_next_line()
                _.cycle_count -= 1


    @property
    def current_namespace(_) -> dict:
        return _.temp_namespaces if _.temp else _.namespaces


    @property
    def current_reserved(_) -> dict:
        return _.temp_reserved if _.temp else _.reserved


    def execute_next_line(_) -> None:
        try: _.code[0]
        except IndexError:
            log('End of file reached')
            _.interpreting = False
            return

        _.current_line_index += 1

        while _.code[0] == '' or _.code[0] == '\n':
            _.code = _.code[1:]
        
        log(f'Parsing Line: {_.code[0]}', important=True)
        _.return_item = _.parse()

        if _.return_item:
            log(f'Return item: {_.return_item}', important=True)

        return _.return_item
            

    def parse(_) -> P_Object:
        line_length = len(_.code[0])
        counts = {
            '{':0,
            '(':0,
        }
        for index in range(line_length):
            char:str = _.code[0][index]
            if char in counts:
                counts[char] += 1
                continue
            if char == '=' and sum(counts.values()) == 0:
                info("Assignment detected")
                _.code = _.code[1:]
                return ... # this is return the parse_assignment, i think

            potential:str = _.code[0][:index+1]
            info(f'potential: {potential}')
            if potential in _.current_reserved:
                _.current_reserved[potential](index)


    
    def parse_assignment() -> P_Object:
        return ...
    

    def parse_function(_, header_end_index:int) -> P_Object:
        leftover = _.code[0][header_end_index+1:]
        leftover_len = len(leftover)
        tokens = []
        open_bracket_count = 0
        close_bracket_count = 0
        open_brace_count = 0
        close_brace_count = 0
        current_index = 0
        return_variable = None
        in_quote = False
        str_stack = ''

        function_name = None
        while current_index < leftover_len:
            char = leftover[current_index]
            if char == '(':
                current_index += 1
                open_brace_count += 1
                function_name = str_stack
                tokens.append(function_name)
                str_stack = ''
                break
            elif char in ['"', "'"]:
                in_quote = not in_quote
                str_stack += char
            elif char == ' ' and in_quote:
                str_stack += char
            elif char not in [' ', '\t']: str_stack += char
            current_index += 1
        
        params = []
        while current_index < leftover_len:
            char = leftover[current_index]
            if char == ',':
                params.append(str_stack)
                str_stack = ''
            elif char == ')':
                params.append(str_stack)
                str_stack = ''
                current_index += 1
                break
            elif char in ['"', "'"]:
                in_quote = not in_quote
                str_stack += char
            elif char == ' ' and in_quote:
                str_stack += char
            elif char not in [' ', '\t']: str_stack += char
            current_index += 1
        
        tokens.append(params)

        block = []
        line_count = 0
        current_index += 3
        while line_count < len(_.code):
            current_line = _.code[line_count]
            current_line_length = len(current_line)
            while current_index < current_line_length:
                char = current_line[current_index]
                if char == '{':
                    if return_variable == None and str_stack != '':
                        return_variable = str_stack
                        tokens.append(return_variable)
                        str_stack = ''
                    open_bracket_count += 1
                    if open_bracket_count > 1:
                        str_stack += char
                elif char == '}':
                    close_bracket_count += 1
                    if open_bracket_count == close_bracket_count:
                        break
                    else:
                        str_stack += char
                elif char == '\n' or char == ';':
                    if str_stack != '':
                        block.append(str_stack)
                    str_stack = ''
                elif char in ['"', "'"]:
                    in_quote = not in_quote
                    str_stack += char
                elif char == ' ' and in_quote:
                    str_stack += char
                elif char not in [' ', '\t']: str_stack += char
                current_index += 1
            current_index = 0
            line_count += 1

        tokens.append(block)

        info(f'tokens: {tokens}')
        info(f'Leftover function contents: {leftover}')
        return ...