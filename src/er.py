"""
Responsible for handling Errors
"""




def fatals(ErrorMessage):
    """
    Generic Fatal Message
    """
    print(ErrorMessage)
    quit()

def fatalc(LineNo, c, expectedC):
    """
    Error on match input with expected char
    """
    print("Error on line", LineNo, " With input", c, " Expected ", expectedC)
    quit()
