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

from typing import List, Callable


class Interpreter:
    code:List[str]
    keywords:dict[str,Callable]
    def __init__(_, code:List[str]=None) -> None:
        _.code = code
        _.interpreting = True
        _.unbounded_cycle_count = 32
        _.reserved = {
            '=':_.parse_assignment,
            'fnc':_.parse_function,
            'obj':_.parse_object,
        }

        while _.interpreting and _.unbounded_cycle_count != 0:
            _.execute_next()
            _.unbounded_cycle_count -= 1


    def execute_next(_) -> None:
        try:
            line = _.code[0]
        except IndexError:
            print('End of File reached')
            _.interpreting = False
            return
        if len(line) != 0:
            print(f'Parsing Line: {line}')
            _.parse(line)
        else:
            _.code.pop(0)


    def parse(_, line:str):
        '''
        parsing rules:
        - anything not wrapped in (), [], or {} is separated by spaces,
        all newlines are replaced with spaces, and duplicate
        spacing is reduced to a single space

        multi-line, (), [] and {} are used for parsing:
            - function declaration
            - class declaration
            - function call
            - class instantiation
        '''
        parsed = []

        # search for keywords
        for count, character in enumerate(line):
            potential_keyword = line[:count]
            if character == '~':
                try:
                    _.reserved[potential_keyword]()
                    return
                except Exception as e:
                    print(f'Falty code before comment:\n{e}')
                
            if character == ' ':
                print(f"keyword: {potential_keyword}")
                try:
                    _.reserved[potential_keyword]()
                    return
                except Exception as e: pass

            try:
                _.reserved[character]()
                return
            except Exception as e: pass


    def parse_assignment(_):
        assignment = _.code[0]
        print(f'Assignment contents:{assignment}')
        _.code = _.code[1:]


    def parse_function(_):
        # we need to track if there's an inner function, or object that requires bracket syntax
        required_brackets:int = 0
        for count, line in enumerate(_.code[1:]):
            if '{' in line: required_brackets += 1
            if '}' in line:
                if required_brackets == 0:
                    content = ''.join(_.code[:count+2])
                    _.code = _.code[count+2:]
                else:
                    required_brackets -= 1
        print(f'Function contents:{content}')

    def parse_object(_):
        # we need to track if there's an inner function, or object that requires bracket syntax
        required_brackets:int = 0
        for count, line in enumerate(_.code[1:]):
            if '{' in line: required_brackets += 1
            if '}' in line:
                if required_brackets == 0:
                    content = ''.join(_.code[:count+2])
                    _.code = _.code[count+2:]
                else:
                    required_brackets -= 1
        print(f'Object contents:{content}')
