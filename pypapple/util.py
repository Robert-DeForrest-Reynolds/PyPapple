from os import environ


BLACK   = '\033[30m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
BLUE    = '\033[34m'
MAGENTA = '\033[35m'
CYAN    = '\033[36m'
WHITE   = '\033[37m'
RESET = '\033[0m'


__all__ = ['log', 'error', 'info']


def log(msg:str, important:bool=False) -> None:
    try:
        if environ['dev'] == 'important' or important:
            print(f'{YELLOW}{msg}{RESET}\n')
        elif environ['dev'] == 'log' or environ['dev'] == 'verbose':
            print(f'{GREEN}{msg}{RESET}\n')
    except: pass


def info(msg:str):
    try:
        if environ['dev'] == 'verbose':
            print(f'{BLUE}{msg}{RESET}\n')
    except: pass


def error(msg:str, line:int=None):
    if line:
        print(f'{RED}Error at Line {line}:{RESET}\n{msg}\n')
    else:
        print(f'{RED}Error:{RESET}\n{msg}\n')
    exit(0)