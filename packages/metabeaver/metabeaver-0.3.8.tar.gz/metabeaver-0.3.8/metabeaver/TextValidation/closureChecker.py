# Takes a string and determines whether the brackets are closed with matching pairs
def is_valid(s: str) -> bool:

    openCloseDict = {
        '(' : ')',
        '[' : ']',
        '{' : '}',
    }

    validString = True

    # List to establish the ordered series of closure we expect to encounter
    closeQueue = []
    for eachChar in s:

        # If we expect a close character but encounter the wrong close, return False - the string is invalid
        if eachChar in openCloseDict.values():
            if closeQueue[-1] != eachChar:
                validString = False
                return validString

        # If we encountered the correct close character, shorten the list of expected characters
        if eachChar in openCloseDict.values():
            if closeQueue[-1] == eachChar:
                closeQueue = closeQueue[0:-1]

        # If we encounter a new opening character, added the expected close character to the queue
        if eachChar in openCloseDict.keys():
            closeQueue.append(openCloseDict.get(eachChar))

    # Will return True, unless we returned false wherein we encountered an unexpected closing char
    return validString



print(is_valid("()"))  # Output: True
print(is_valid("()[]{}"))  # Output: True
print(is_valid("(]"))  # Output: False
print(is_valid("([)]"))  # Output: False
print(is_valid("{[]}"))  # Output: True