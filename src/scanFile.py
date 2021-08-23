"""
This file is respoisble for
reading the file
scanning the contents of the file
"""
import er
from token import isToken, token
#this will hold the current character we are scanning
global_filetext = None
global_c = None
global_fileInput = -2
global_Line = 0

#Tokens Dictionaries
declaredTokens = {} # of form "Token name" : TypeEnum
productions = {} # of form productions[head] = [array where each element is what is next], array of array for multiple elemnts

def scan():
    """
    This will use some syntax directed traslation in order to achive our goal
    """
    #we must first match a "%start" as the first line
    next(True)
    #print("Now Match %start\n")
    matchLine("%start")
    tokens()
    next(True)
    matchLine("%grammar")
    #print(declaredTokens)
    grammar()
    return productions


#------------------------------------------------------------------------
def tokens():
    """
    This will scan all tokens until we reach the %grammar line
    """
    next(True)
    while(lookahead("%grammar") == False):
        scanToken()
    #print("We Found %grammar")

def scanToken():
    """
    Syntax directed translation of a token line
    %token <tokentype> identifierForToken
    """
    matchString("%token")
    #print(f"Retard?, gl_c=\"{global_c}\"")
    next(True)
    #print(f"Lets match, gl_c=\"{global_c}\"")
    matchC("<")
    # we want to match anystring of [a-zA-Z]
    tokentype = matchStringAlpha()
    matchC(">")
    next(True)
    identifier = matchStringAlpha_()
    next(False, "\n")
    matchC("\n")
    #print(f"We Found a Token WOOOO like %token <{tokentype}> {identifier} \\n")
    #Lets insert the token HERE and check tokenTypes and ids to make sure not clashing
    #----
    valid, value = isToken(tokentype)
    if(valid):
        declaredTokens[identifier] = value
    else:
        er.fatals(f"ERROR, Invalud tokentype on line {global_Line} of declared type {tokentype}")
    #----

def grammar():
    """
    This will scan grammar
    """
    next(True)
    #First Match %aug : productionID \n
    #   ;
    matchString("%aug")
    next(False)
    matchC(":")
    next(False)
    identifier = matchStringAlpha_()
    initProduction("%aug")
    addBodyToProductionHead("%aug",  [(identifier, token.PRODUCTION)])
    matchC("\n")
    if(isWaste(global_c)):
        next(True)
    matchLine(";")
    if(isWaste(global_c)):
        next(False)
    #print("Found the first augmentation of the grammar")
    #print(productions)
    while(lookahead("%end") == False):
        scanProduction()
        #print(productions)
    matchString("%end")
    #print("We found %end")

def scanProduction(template = []):
    """
    We Will scan production
    """
    #look for head
    #print("LETS START A PRODUCTION, ", global_c)
    if(isWaste(global_c)):
        next(False)
    head = matchStringAlpha()
    #print(f"FOUND HEAD, \"{head}\"")
    initProduction(head)
    next(False)
    matchC(":")
    next(False)
    # Now we must scan
    # Note!!!!! if we scan a \' then we know we must be scanning a char then \' everthing else
    # will be as keyword defs
    body = []
    while(True):
        #print("~~~~~~~~Iter : ", productions, " Current body = ", body)
        if(lookCurrent("\n")):
            #match it
            matchC("\n")
            next(False)
            #print("--\t\t adding body ", body, "to ", head)
            if(body != []):
                addBodyToProductionHead(head, body)
            body = []
            continue
        if(lookCurrent(";")):
            #match it
            matchC(";")
            next(True)
            #print("--\t\t adding body ", body, "to ", head)
            if(body != []):
                addBodyToProductionHead(head, body)
            #print("~~~~~~~~~~~~~~~~~~~~~~~~ We finished this one")
            return
        if(lookCurrent("|")):
            #match it and ignore it
            matchC("|")
            #print("--\t\t adding body ", body, "to ", head)
            if(body != []):
                addBodyToProductionHead(head, body)
            body = []
            next(False)
            continue
        if(lookCurrent("\'")):
            # we are gonna match a char
            # match it
            matchC("\'")
            #we must match a char next
            c = global_c
            getnext()
            matchC("\'")
            next(False)
            body.append((c, token.CHAR))
            continue
        #else then we must be matching a
        identifier = matchStringAlpha_()
        body.append((identifier, declaredTokens[identifier]))
        next(False)


#------------------------------------------------------------------------

def isIdentifierType(identifier, expectedTokenType):
    """
    Checks if it is of type
    """
    if(identifier == "%aug" and expectedTokenType == token.PRODUCTION):
        return
    if(identifier in declaredTokens):
        if(declaredTokens[identifier] != expectedTokenType):
            er.fatals(f"Declared token {identifier} declared as {declaredTokens[identifier]} not {expectedTokenType}")
    else:
        er.fatals(f"Identifier {identifier} not declared in %tokens section above")

def initProduction(productionHead):
    isIdentifierType(productionHead, token.PRODUCTION)
    if(productionHead in productions):
        er.fatals(f"Production Head {productionHead} is already used, please use another alias for head in Line {global_Line}")
    productions[productionHead] = []

def addBodyToProductionHead(head, body):
    """
    Body must be ["element", "char", "Scanned in shit"]
    No new line is needed at the end
    """
    if(head not in productions):
        er.fatals(f"Ok man what the fuck, {head} is not a valid production head")
    productions[head].append(body)

#------------------------------------------------------------------------

def match(toMatchC):
    #print("- Trying to match characters gl_c=", global_c, " s[i] =",toMatchC)
    global global_Line
    if(global_c == toMatchC):
        if(global_c == "\n"):
            global_Line += 1
        return True
    return False

def matchC(c):
    #print(f"TRYING TO MATCH CHAR, gl_c=\"{global_c}\"")
    if(match(c) == False):
        er.fatalc(global_Line, global_c, c)
    getnext()
    #print("WHA")

def matchString(string):
    for c in string:
        if(match(c) == False):
            er.fatalc(global_Line, global_c, c)
        getnext()
    #print("Matched ", string, "Perfectly")
    #hence string is matched
    #ending with global_c = on char just after string in file

def matchLine(string):
    matchString(string)
    err = False
    if( match("\n")):
        #print("Matched Line perfectly of ", string)
        return
    next(False)
    if( match("\n") == False):
        er.fatalc(global_Line, global_c, "\n")
    #print("Matched Line perfectly of ", string)

def matchStringAlpha():
    """
    Scans Regex Equivilant of [a-zA-Z]
    """
    identifier = ""
    while(global_c.isalpha()):
        #print(f"global_c = \'{global_c}\'")
        identifier += global_c
        getnext()
    #print(f"Found identifier = \"{identifier}\"" )
    return identifier

def matchStringAlpha_():
    """
    Scans Regex Equivilant of [a-zA-Z]
    """
    identifier = ""
    while(global_c.isalpha() or global_c == "_"):
        #print(f"global_c = \'{global_c}\'")
        identifier += global_c
        getnext()
    #print(f"Found identifier = \"{identifier}\"" )
    return identifier

def lookahead(lookahead):
    tempPos = global_fileInput
    if(isWaste(global_c)):
        next(True)
    if(global_fileInput + len(lookahead) <= len(global_filetext)):
        #print(f"LOOKAHEAD FOR \"{lookahead}\" , \"{global_filetext[global_fileInput: global_fileInput + len(lookahead)]}\"")
        if(global_filetext[global_fileInput: global_fileInput + len(lookahead)] == lookahead):
            setGlobalPos(tempPos)
            return True
    setGlobalPos(tempPos)
    return False

def lookCurrent(lookahead):
    if(lookahead == global_c):
        return True
    return False

def isWaste(c):
    if(global_c == " " or global_c == "\t" or global_c == "\n"):
        return True
    return False



def getnext():
    """
    Gets the next character in the text no matter what it is
    """
    global global_fileInput, global_c, global_filetext
    global_fileInput += 1
    if(global_fileInput == len(global_filetext)):
        #print("Done")
        return
    global_c = global_filetext[global_fileInput]
    #print("Next = \"", global_c,"\"", global_fileInput, ord(global_c))

def putback():
    """
    Put back character of importance
    """
    global global_fileInput, global_c, global_filetext
    global_fileInput -= 1
    global_c = global_filetext[global_fileInput]

def setGlobalPos(pos):
    global global_fileInput, global_c
    global_fileInput = pos
    global_c = global_filetext[global_fileInput]
    #print("reset to ", global_c)

def next(incNewLine, lookfor = chr(0)):
    """
    Gets the next character of value
    Anything that is NOT (" ", \t, \r)
    or includes \n
    """
    global global_Line
    change = 0
    if(global_c == lookfor):
        return
    getnext()
    #print(f"-nex-ed, gl_c=\"{global_c}\"")
    while(global_c == " " or global_c == "\t" or (incNewLine & (global_c == "\n") ) ):
        if(global_c == "\n"):
            global_Line += 1
        change += 1
        getnext()
    #print(f"--Fnex-ed, gl_c=\"{global_c}\"{change}")

    #so now global_c has a non shit value we can now work with

def readFrom(filename):
    """
    This reads the files contents and returns it
    """
    F = open(filename, 'r')
    text = F.read().strip()
    F.close()
    global global_filetext, global_c
    global_filetext = text
    #print(global_filetext)
    #print("----------------------------------------- END FILE")
    next(False) # Init the first variable


def scanFrom():
    readFrom("grammar.txt")
    scannedProductions = scan()
    return scannedProductions

if __name__ == "__main__":
    readFrom("grammar.txt")
    scannedProductions = scan()
