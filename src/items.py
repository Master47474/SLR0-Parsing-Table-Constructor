"""
This class handles the item and its structure
"""
from token import token

productions = {}

def initProductions(incomingProd):
    global productions
    productions = incomingProd

class item():
    def __init__(self, head, body, cPos, initClosure=False):
        self.head = head
        self.body = body
        self.cPos = cPos #0 indexed so if at 0 it is the 0th index, if it len(body) it is after the last token
        self.closure = {}
        if(initClosure):
            self.makeClosure()
        self.gotos = {}


    def makeClosure(self):
        #lets get what we are currently seeing next
        nextToken = self.getTokenAtCPos()
        self.aux_makeClosure(nextToken)

    def aux_makeClosure(self, followHead):
        if(followHead == None):
            return
        if(followHead[0] in self.closure):
            return
        if(followHead[1] != token.PRODUCTION):
            return
        #Only know what to do if it a production
        for productionBody in productions[followHead[0]]:
            itemFound = item(followHead[0], productionBody, 0)
            self.addToClosure(followHead[0], itemFound)
        for bodyItem in self.closure[followHead[0]]:
            self.aux_makeClosure(bodyItem.getTokenAtCPos())

    def getTokenAtCPos(self):
        if(self.cPos == len(self.body)): #i.e E : A B C D + .
            return None
        else:
            return self.body[self.cPos]

    def addToClosure(self, head, bodyItem):
        if(head not in self.closure):
            self.closure[head] = []
        self.closure[head].append(bodyItem)

    def GOTO(self):
        gotos = {}
        gotos[self.getTokenAtCPos()] = []
        for head in self.closure:
            for itemClosure in self.closure[head]:
                gotos[itemClosure.getTokenAtCPos()] = []
        # Lets first Check self
        if(self.getTokenAtCPos() in gotos):
            gotos[self.getTokenAtCPos()].append(self.goNext())
        #we want to get all transitions from each item in closure
        for head in self.closure:
            for itemClosure in self.closure[head]:
                gotos[itemClosure.getTokenAtCPos()].append(itemClosure.goNext())
        return gotos


    def goNext(self, doClosure = True):
        if(self.cPos == len(self.body)):
            return None
        return item(self.head, self.body, self.cPos + 1, doClosure)

    def getAll(self):
        new = self.closure
        new[self.head] = [self]
        return new

    def EqualProduction(self, other):
        if not isinstance(other, item):
            return False
        return (self.head == other.head and self.body == other.body)

    def __repr__(self):
        st = ""
        for i,e in enumerate(self.body):
            if i == self.cPos:
                st += "."
            st += e[0]
        if(self.cPos == len(self.body)):
            st += "."
        return st

    def __str__(self):
        st = self.head + ":"
        for i,e in enumerate(self.body):
            if i == self.cPos:
                st += "."
            st += e[0]
        if(self.cPos == len(self.body)):
            st += "."
        return st

    def normalStr(self):
        st = self.head + ":"
        for i,e in enumerate(self.body):
            st += e[0]
        return st

    def __eq__(self, other):
        if not isinstance(other, item):
            return False
        return (self.head == other.head and self.body == other.body and self.cPos == other.cPos)
