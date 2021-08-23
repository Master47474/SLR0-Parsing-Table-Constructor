"""
This handles everything
"""
from scanFile import scanFrom
from items import item, initProductions
from token import token, SerializeTokenHelper
import json

# Istates is of form
# State is the key (0,1,2,3,4 ...)
# Contents ([key productions])
Istates = {}
CurrentIndex = 0
productionsForTable = []
table = {} # array of dictioanaries
singleTokens = {}

def consumeGoto(gotos):
    """
    This Consumes a goto dinctionary into the states dictionary
    """
    global CurrentIndex
    for head in gotos:
        #Make a new state with the items of gotos[head] as its value
        found = False
        for i in range(CurrentIndex):
            if (checkSetsOfItems(Istates[i], gotos[head]) == True):
                found = True
                break
        if(found == True):
            found = False
            continue
        Istates[CurrentIndex] = gotos[head]
        CurrentIndex += 1

def checkSetsOfItems(set1, set2, atLeastOne = False):
    if len(set1) != len(set2) and atLeastOne == False:
        return False
    matches = [0] *len(set1)
    i = 0
    for itX in set1:
        for itY in set2:
            matches[i] |= (itX == itY)
        i += 1
    if(atLeastOne == True):
        for m in matches:
            if m == 1:
                return True
        return False
    else:
        for m in matches:
            if m == 0:
                return False
        return True

def findInIstate(itemsArr):
    for i in range(CurrentIndex):
        if (checkSetsOfItems(Istates[i], itemsArr, True) == True):
            return i
    return -1

def getItemProductionIndex(item):
    i = 0
    for prodItem in productionsForTable:
        if( prodItem.EqualProduction(item) ):
            return i
        i += 1
    #for safe keeping tho
    return -1 #!!!! cant ever have this as a return value. is everything else working??

def constructTable(startItem):
    for Ii in Istates:
        table[Ii] = {}
        for item in Istates[Ii]:
            togoThrough = item.getAll()
            for head in togoThrough:
                for current in togoThrough[head]:
                    tokenCur = current.getTokenAtCPos()
                    #SHIFT to another state
                    curNext = current.goNext(False)
                    # now find this in Istates
                    if(curNext == None):
                        if(current == startItem.goNext(False)):
                            table[Ii][(None, token.ACCEPT)] = -1
                        else:
                            #we should reduce now
                            r = getItemProductionIndex(current)
                            table[Ii][tokenCur] = (token.REDUCE, r)
                        continue
                    j = findInIstate([curNext])
                    if(j == -1):
                        er.fatals(f"{curNext} was not found in Istates, how does this happen?")
                    else:
                        identiToken = token.SHIFT
                        if(tokenCur[1] == token.PRODUCTION):
                            identiToken = token.GOTO
                        table[Ii][tokenCur] = (identiToken, j)

if __name__ == "__main__":
    scannedProductions = scanFrom()
    initProductions(scannedProductions)
    # we now get the %aug production and work from there as a start point
    startItem = item("%aug", scannedProductions["%aug"][0], 0, True)
    Istates[CurrentIndex] = [startItem]
    CurrentIndex += 1
    gotos = startItem.GOTO()
    consumeGoto(gotos)
    i = 1
    while(i < CurrentIndex):
        for oneItem in Istates[i]:
            itemGoto = oneItem.GOTO()
            if( None in itemGoto ):
                continue
            consumeGoto(itemGoto)
        i += 1
    #So now lets make the parsing table
    #Consutrt Table for refering reductions
    all = startItem.getAll()
    for head in all:
        for item in all[head]:
            productionsForTable.append(item)
    constructTable(startItem)
    #Lets make sense of our table so far
    #if we have a shift or goto of a prodution or char then it will have its own respective entrt as (token, token.VALUE ) as a key
    # if not then check if there exists a None: which will contain an reduction
    for head in scannedProductions:
        for tokensScanned in scannedProductions[head]:
            for singTok in tokensScanned:
                if (singTok[1] not in singleTokens):
                    singleTokens[singTok[1]] = {}
                if(singTok not in singleTokens[singTok[1]]):
                    singleTokens[singTok[1]][singTok] = 1

    # LETS FORMAT THIS AND PRING IT
    jsonTable = {}
    for symbol in singleTokens:
        if symbol != token.PRODUCTION:
            for singTok in singleTokens[symbol]:
                jsonTable[singTok[0]] = {}
    for symbol in singleTokens:
        if symbol == token.PRODUCTION:
            for singTok in singleTokens[symbol]:
                jsonTable[singTok[0]] = {}

    for i in range(CurrentIndex):
        for symbol in singleTokens:
            if symbol != token.PRODUCTION:
                for singTok in singleTokens[symbol]:
                    jsonTable[singTok[0]][i] = {}
                    jsonTable[singTok[0]]["type"] = SerializeTokenHelper(singTok[1]).makeSerealizable()
                    if(singTok not in table[i]):
                        if( None in table[i] ):
                            #then we can reduce here
                            jsonTable[singTok[0]][i] = f"r{table[i][None][1]}"
                        else:
                            #then we dont have anything, keep it blank
                            jsonTable[singTok[0]][i] = f"-1"
                    else:
                        #so we shifting
                        action, stateIndex = table[i][singTok]
                        jsonTable[singTok[0]][i] = f"s{stateIndex}"
        for symbol in singleTokens:
            if symbol == token.PRODUCTION:
                for singTok in singleTokens[symbol]:
                    jsonTable[singTok[0]][i] = {}
                    jsonTable[singTok[0]]["type"] = SerializeTokenHelper(singTok[1]).makeSerealizable()
                    if(singTok not in table[i]):
                        jsonTable[singTok[0]][i] = f"-1"
                        continue
                    #so we shifting
                    action, stateIndex = table[i][singTok]
                    jsonTable[singTok[0]][i] = f"{stateIndex}"
    #we also need the transitions
    reducedTransision = { i: trans for i,trans in enumerate(list(map(lambda x: x.normalStr().split(":"), productionsForTable)))}
    with open('slr0_table.json', 'w') as file:
        file.write(json.dumps({"Reduce Transitions":  reducedTransision}, indent=4))
        file.write(json.dumps({"Table":  jsonTable}, indent=4))
