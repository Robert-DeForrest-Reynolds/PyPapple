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


BLACK   = '\033[30m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
BLUE    = '\033[34m'
MAGENTA = '\033[35m'
CYAN    = '\033[36m'
WHITE   = '\033[37m'
RESET = '\033[0m'


class Object:
    name:str
    value:Any
    def __init__(_, name):
        log("Instantiating Object")
        _.name = name


def log(msg:str, important:bool=False) -> None:
    if important:
        print(f'{YELLOW}{msg}{RESET}\n')
    else:
        print(f'{GREEN}{msg}{RESET}\n')


def error(msg:str, line:int=None):
    if line:
        print(f'{RED}Error at Line {line}:{RESET}\n{msg}\n')
    else:
        print(f'{RED}Error:{RESET}\n{msg}\n')


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
        assignee:Object
        if _._try(lambda: _.namespaces[assignee_name]):
            assignee = _.namespaces[assignee_name]
        else:
            _.namespaces.update({assignee_name:Object(assignee_name)})
            assignee = _.namespaces[assignee_name]
            log(f'Assigning new namespace: {assignee_name}')
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