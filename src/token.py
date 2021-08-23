"""
This file contains functions that are used to determine token type
and Functions to determine what a token is
"""
from enum import Enum, auto

class SerializeTokenHelper():
    def __init__(self, token):
        self.token = token

    def makeSerealizable(self):
        return self.token.name

class token(Enum):
    PRODUCTION = auto()
    KEYWORD = auto()
    NVALUE = auto()
    IVALUE = auto()
    CHAR = auto()
    # FOR parsing table
    ACCEPT = auto()
    REDUCE = auto()
    SHIFT = auto()
    GOTO = auto()

types = [("production", token.PRODUCTION), ("keyword", token.KEYWORD), ("nValue", token.NVALUE), ("iValue", token.IVALUE)]


def isToken(keyword):
    #print(f"\"{keyword}\"")
    for i in range(0, len(types)):
        if(keyword == types[i][0]):
            return (True, types[i][1])
    return (False, -1)
