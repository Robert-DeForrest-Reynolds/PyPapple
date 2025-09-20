"""
minimal implementation requirements:
 - the syntax in full implementation
 - the language should feel like it will when written in full using C
 - thought-through implementation of error handling
 - a LSP for vscode so the language can actually be used

what does not need to be in the language:
 - standard library implementations Python already handles (string manipulation, packing/unpacking or structuring/destructuring, etc.)
 - quality of life implementations that are not paramount to the fundamental developer workflow
 - anything not really in the tech_doc.md
"""

from typing import List, Callable


class Interpreter:
    code:List[str]
    keywords:dict[str,Callable]
    def __init__(_, code:List[str]) -> None:
        _.code = code
        _.interpreting = True
        _.reserved = {
            "=":_.parse_assignment,
            "fnc":_.parse_function,
            "obj":_.parse_object,
        }

        while _.interpreting:
            _.execute_next()


    def execute_next(_) -> None:
        try:
            line = _.code[0]
        except IndexError:
            print("End of File reached")
            _.interpreting = False
            return
        if len(line) != 0:
            print(f"Parsing Line: {line}")
            _.parse(line)
        else:
            _.code.pop(0)


    def parse(_, line:str):
        """
        parsing rules:
        - anything not wrapped in (), [], or {} is separated by spaces,
        all newlines are replaced with spaces, and duplicate
        spacing is reduced to a single space

        multi-line, (), [] and {} are used for parsing:
            - function declaration
            - class declaration
            - function call
            - class instantiation
        """
        parsed = []

        # search for keywords
        for count in range(len(line)):
            potential_keyword = line[:count+1]
            try:
                _.reserved[potential_keyword]()
                return
            except Exception as e:
                pass

        for character in line:
            try:
                _.reserved[character]()
                return
            except Exception as e:
                pass


    def parse_assignment(_):
        assignment = _.code[0]
        print(assignment)
        _.code = _.code[1:]


    def parse_function(_):
        content:str
        for count, line in enumerate(_.code):
            if "}" in line:
                content = "".join(_.code[:count+1])
                _.code = _.code[count+1:]
        print(f"Function contents:{content}")

    def parse_object(_):
        ...



example_syntax = """\
x = 10
"""
