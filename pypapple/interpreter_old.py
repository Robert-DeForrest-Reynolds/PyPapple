from typing import Callable, Any
from os import environ
from sys import getrecursionlimit, setrecursionlimit

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

        _.namespaces = {}
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
            'in':_.parse_call,

            '=':_.parse_assignment,
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
                _.execute_next()
        else:
            while _.interpreting and _.cycle_count != 0:
                _.execute_next()
                _.cycle_count -= 1

    @property
    def current_namespace(_) -> dict:
        return _.temp_namespaces if _.temp else _.namespaces


    @property
    def current_reserved(_) -> dict:
        return _.temp_reserved if _.temp else _.reserved
        

    def execute_next(_) -> None:
        try: _.code[0]
        except IndexError:
            log('End of file reached')
            _.interpreting = False
            return

        _.current_line_index += 1

        if _.code[0] == '' or _.code[0] == r'\n':
            _.code = _.code[1:]
            return
        
        log(f'Parsing Line: {_.code[0]}', important=True)
        _.return_item = _.parse()

        if _.return_item:
            log(f'Return item: {_.return_item}', important=True)

        return _.return_item


    def execute_function_body(_, f:Function, args:list) -> Any:
        log(f'Executing: {f.name}')
        storage = _.code.copy()
        _.code = f.block
        _.temp = True
        _.temp_namespaces = f.namespaces
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
        
        return _.return_item


    def parse(_):
        # Remove comments from line
        code = _.code[0].split("~")[0].strip()
        if len(code) == 0:
            log("Ignoring comment")
            _.code = _.code[1:]
            return

        # catches all space separated reserves
        potential = code.split(" ")[0].strip()
        if potential in _.reserved:
            return _.reserved[potential]()
        elif potential in _.temp_reserved:
            return _.temp_reserved[potential]()

        # catch calls
        potential = code.split("(")[0].strip()
        if potential in _.reserved:
            return _.reserved[potential]()
        elif potential in _.temp_reserved:
            return _.temp_reserved[potential]()

        # catch assignments, do this last as it's the heaviest
        for char in code:
            if char == '=':
                return _.parse_assignment()
        
        
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
                if operative[0] in ["'", '"'] or operative.isdigit():
                    evaluation += operative + char
                elif operative in _.current_namespace:
                    operative = _.current_namespace[operative].value
                    evaluation += operative + char

            elif index == expr_len:
                operative = expr[last_addition_index+1:].strip()
                if operative in _.current_namespace:
                    operative = _.current_namespace[operative].value
                evaluation += operative
        
        log(f'Expression evaluation: {evaluation}')
        try:
            if assignee:
                assignee.value = str(eval(evaluation))
                return assignee
            else:
                p_object = P_Object("eval_var")
                p_object.value = str(eval(evaluation))
            log("Evaluation Successful")
            return p_object
        except Exception:
            log("Evaluation Unsuccessful")
            return None


    def parse_assignment(_):
        assignment = _.code[0].strip().split('=')
        assignee_name:str = assignment[0].strip()
        assignee:P_Object
        
        if assignee_name in _.current_namespace:
            assignee = _.current_namespace[assignee_name]
        else:
            _.current_namespace.update({assignee_name:P_Object(assignee_name)})
            assignee = _.current_namespace[assignee_name]
        assignment_str = assignment[1].strip()

        if assignment_str in _.current_namespace:
            assignee.value = _.current_namespace[assignment_str]

        # catch calls, and operations
        # needs to check if instantiation still
        potential = assignment_str.split("(")[0].strip()
        result = None
        if potential in _.reserved:
            result = _.reserved[potential]()
            assignee.value = result
        elif potential in _.temp_reserved:
            result = _.temp_reserved[potential]()
            assignee.value = result
        else:
            new_assignee:P_Object = _.evaluate_expression(assignment_str, assignee=assignee)
            if new_assignee:
                _.current_namespace[assignee_name] = new_assignee

            else: assignee.value = assignment_str
        
        info(f'Assignment contents: name=`{assignee_name}`, value=`{assignee.value}`\n')
        info(f'Assignment Object: {assignee}')
        _.code = _.code[1:]
        return result


    def parse_function(_):
        signature, content = _.find_closing_symbol("{", "}")
        info(f'Function signature: {signature}\n')
        info(f'Function contents: {content}\n')

        f = Function(signature, content)
        
        _.reserved.update({f.name:_.parse_call})
        _.namespaces.update({f.name:f})


    def parse_object(_):
        signature, content = _.find_closing_symbol("{", "}")
        info(f'Object signature: {signature}\n')
        info(f'Object contents: {content}\n')


    def parse_try(_):
        signature, content = _.find_closing_symbol("{", "}")
        info(f'Try contents: {content}\n')


    def parse_for(_):
        signature, content = _.find_closing_symbol("{", "}")
        info(f'For signature: {signature}\n')
        info(f'For contents: {content}\n')


    def parse_while(_):
        signature, content = _.find_closing_symbol("{", "}")
        info(f'While signature: {signature}\n')
        info(f'While contents: {content}\n')


    def parse_if(_):
        signature, content = _.find_closing_symbol("{", "}")
        info(f'If signature: {signature}\n')
        info(f'If contents: {content}\n')


    def parse_call(_):
        signature, content = _.find_closing_symbol("(", ")")
        if '=' in signature: # check if function call is assignment
            signature = signature[signature.find('=')+1:].strip()
        info(f'Call signature: {signature}\n')
        info(f'Call contents:{content}\n')
        
        passed_arguments = []
        last_comma_index = 0
        required = 0
        required_type = ""

        for index, c in enumerate(content[0]):
            if c == required_type:
                required -= 1
            elif c in ['"', "'"]:
                required_type = c
                required += 1
                
            if c == ',' and required == 0:
                passed_arguments.append(content[0][last_comma_index:index].strip())
                last_comma_index = index

        if required == 0 and passed_arguments == []:
            passed_arguments.append(content[0])
        else:
            leftover = content[0][last_comma_index+1:]
            passed_arguments.append(leftover)

        if signature in _.current_namespace:
            f:Function = _.current_namespace[signature]()
            arg_count = len(f.namespaces.keys())

            index = 0
            for name, value in f.namespaces.items():
                if index == arg_count: break
                if value == None:
                    f.namespaces[f.arguments[index]] = P_Object(name, passed_arguments[index])
                    index += 1
                    continue

            result = _.execute_function_body(f)
            return result
        elif signature in _.callables:
            result = _.callables[signature](passed_arguments)
            info(f'Callable return: {result}')
            return result