from typing import Callable, Any
from os import environ
from sys import setrecursionlimit, getrecursionlimit

from .util import *
from .standard import *
from .p_object import P_Object
from .function import Function


__all__ = []


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
        _.header = {
            # separation with a space is required
            'fnc':_.parse_function,
            'obj':lambda: info("obj decl found"),
            'try':lambda: info("try found"),
            'for':lambda: info("for found"),
            'if':lambda: info("if found"),
            'while':lambda: info("while found"),
        }

        _.callables = {
            "out":lambda *args: P_out(_, *args),
            "in":lambda *args: P_in(_, *args),
        }

        _.temp = False
        _.temp_function_signature = 'fnc __temp__()'
        _.temp_namespaces:dict[str:P_Object|Function] = {}
        _.temp_callables:dict[str:Function] = {}

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
    def current_namespace(_) -> dict[str:P_Object]:
        return _.temp_namespaces if _.temp else _.namespaces


    @property
    def current_callables(_) -> dict[str:Function|Callable]:
        return _.temp_callables if _.temp else _.callables


    def execute_next_line(_) -> None:
        _.current_line_index += 1

        while _.code:
            if _.code[0] == '' or _.code[0] == '\n':
                _.code = _.code[1:]
            else:
                break

        try: _.code[0]
        except IndexError:
            log('End of file reached')
            _.interpreting = False
            return

        
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
                assignment_result = _.parse_assignment(index)
                return assignment_result

            potential:str = _.code[0][:index+1]
            info(f'potential: {potential}')
            if potential in _.header:
                return _.header[potential](index)
            
            if potential in _.callables:
                return _.parse_call(index, _.callables[potential])


    # does not handle multi-line calls
    def parse_call(_, header_end_index:int, call:Callable) -> P_Object:
        # 2 to skip the paranthesis, as we stop at the end of the name of the call
        leftover = _.code[0][header_end_index+2:]
        leftover_len = len(leftover)
        tokens = []
        current_index = 0
        in_quote = False
        str_stack = ''

        params = []
        
        while current_index < leftover_len:
            char = leftover[current_index]
            if char == ',':
                params.append(str_stack)
                str_stack = ''
            elif char == ')':
                params.append(str_stack)
                tokens.append(params)
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

        result = call(params)

        if leftover[current_index:]:
            _.code[0] = leftover[current_index:]
        else:
            _.code = _.code[1:]

        return result


    # currently the parser only supports single-line assignments
    def parse_assignment(_, equals_index:int) -> P_Object:
        line = _.code[0]
        name = line[:equals_index].strip()
        assignment:str = line[equals_index+1:].strip()

        assignee:P_Object = None

        call_split = assignment.split("(")
        potential_call = call_split[0].strip()
        if potential_call in _.current_callables:
            # need to get arguments line by line, in case it's multiline
            assignment = _.current_callables[potential_call](_, call_split[1][:-1])
        
        if type(assignment) == str:
            for char in assignment:
                if char in ['+', '-', '*', '/']:
                    assignment = _.evaluate_expression(assignment).value
                    break
        if name in _.current_namespace:
            assignee = _.current_namespace[name]
            assignee.value = assignment
        else:
            if assignment.isdigit():
                assignment = int(assignment)
            assignee = P_Object(name, assignment, int)
            _.current_namespace.update({name:assignee})
        _.code = _.code[1:]
        log(f'name: {name}\nassignee: {assignee}\nassignment: {assignment}')
        return assignee
    

    def parse_function(_, header_end_index:int) -> Any:
        leftover = _.code[0][header_end_index+1:]
        leftover_len = len(leftover)
        tokens = []
        open_bracket_count = 0
        close_bracket_count = 0
        current_index = 0
        in_quote = False
        str_stack = ''

        function_name = None
        params = []
        return_variable = False
        block = []

        while current_index < leftover_len:
            char = leftover[current_index]
            if char == '(':
                function_name = str_stack
                tokens.append(function_name)
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
        
        while current_index < leftover_len:
            char = leftover[current_index]
            if char == ',':
                params.append(str_stack)
                str_stack = ''
            elif char == ')':
                params.append(str_stack)
                tokens.append(params)
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

        line_count = 0
        current_index += 3
        parsing = True
        while line_count < len(_.code) and parsing:
            current_line = _.code[line_count]
            current_line_length = len(current_line)
            while current_index < current_line_length:
                char = current_line[current_index]
                if char == '{':
                    open_bracket_count += 1
                    if return_variable == False and str_stack != '':
                        return_variable = str_stack
                        tokens.append(return_variable)
                        str_stack = ''
                    elif open_bracket_count > 1:
                        str_stack += char
                    else:
                        return_variable = None
                        tokens.append(return_variable)
                elif char == '}':
                    close_bracket_count += 1
                    if open_bracket_count == close_bracket_count:
                        parsing = False
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

        f = Function(tokens)

        _.current_callables.update({f.name:f})
        print(_.code)
        print(line_count)
        _.code = _.code[line_count:]
        print(_.code)
        info(f'{function_name}\'s tokens: {tokens}')
        return ...
    

    def execute_function(_, f:Function, args:str):
        log(f'Executing: {f.name}')
        storage = _.code.copy()
        _.code = f.block
        args:list = [arg.strip() for arg in args.split(',')]
        print(_.current_namespace)
        for arg in args:
            if arg in _.current_namespace:
                f.namespaces[arg] = _.current_namespace[arg]
                args.remove(arg)
        for arg in args:
            for k in f.namespaces:
                if f.namespaces[k].value == 'none':
                    f.namespaces[k].value = arg

        _.temp = True
        _.temp_namespaces = f.namespaces
        print(f.namespaces)
        print(f'built namespace: {_.temp_namespaces}')
        _.temp_reserved = f.reserved

        while len(_.code) > 0:
            log(f'Parsing Block Line: {_.code[0]}', important=True)
            _.return_item = _.parse()
            if _.return_item:
                log(f'Return item: {_.return_item}', important=True)

        _.code = storage
        _.temp = False
        _.temp_namespaces = {}
        _.temp_reserved = {}

        if f.return_item != None:
            return f.namespaces[f.return_item].value
        
        print(f'{f.name}\'s execution return: {_.return_item}')
        return _.return_item
    

    def evaluate_expression(_, expr:str, assignee:P_Object=None):
        log(f'Expression expr: {expr}')
        evaluation = ""
        expr_len = len(expr)-1
        last_addition_index = 0
        first_operative = False
        for index, char in enumerate(expr):
            if char in ['+', '-', '*', '/']:
                if not first_operative:
                    operative = expr[:index].strip()
                    first_operative = True
                    last_addition_index = index
                else:
                    operative = expr[last_addition_index+1:index].strip()
                    last_addition_index = index

                if operative[0] in ["'", '"'] and operative[0] == operative[-1] or operative.isdigit():
                    evaluation += operative + char
                elif operative in _.current_namespace:
                    operative = _.current_namespace[operative].out
                    evaluation += operative + char
                else:
                    error(f'Unknown value: `{operative}`')

            elif index == expr_len:
                operative = expr[last_addition_index+1:].strip()
                if operative in _.current_namespace:
                    print(operative)
                    print(_.current_namespace)
                    operative = _.current_namespace[operative].out
                    evaluation += operative
                elif operative.isdigit():
                    evaluation += operative
                else:
                    error(f'Unknown value: `{operative}`')
        
        log(f'Expression evaluation: {evaluation}')
        try:
            if assignee:
                assignee.value = str(eval(evaluation))
                log("Evaluation Successful")
                return assignee
            else:
                p_object = P_Object("eval_var")
                p_object.value = str(eval(evaluation))
                log("Evaluation Successful")
                return p_object
        except Exception:
            log("Evaluation Unsuccessful")
            return None