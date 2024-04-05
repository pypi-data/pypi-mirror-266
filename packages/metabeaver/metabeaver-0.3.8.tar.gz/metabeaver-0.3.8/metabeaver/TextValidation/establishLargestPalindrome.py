# O(N^3) runtime
def findLargestPalindrome(string):

    # String as len(string) factorial combinations
    # Only interested in the combinations minus single letters
    # Therefore, in the event space of consideration, possible states to consider is len(string)! = len(string)

    # Need a function to check whether a string IS a palindrome
    def isPalindrome(string):

        # Assume we have a palindrome until we colide with a mismatch
        defaultAssumption = True

        # Indexer which will update and return characters in reverse to compare to each char of string
        count = 1
        stringLength = len(string)
        for eachChar in string:
            reverseChar = string[(stringLength - count)]
            if eachChar != reverseChar:
                return False
            count += 1

        # If we did not invalidate our naive assumption of palindrominity by proof of contradiction, yay!
        return defaultAssumption

    # Need container for valid combinations in event space that are plaindromes, a subset of the set of combinations
    palindromeList = []

    startSize = 2 # Ignore single letters
    while startSize <= len(string):
        # Start at left hand side of string
        startIndex = 0
        # Proceed in increments of length n, starting at 2, while >= string size, discovering potential plaindromes
        while startSize + startIndex <= len(string):
            currentSegment = string[startIndex: (startIndex + startSize)]
            palindromeCheck = isPalindrome(currentSegment)
            if palindromeCheck:
                palindromeList.append(currentSegment)
            # Increment that length of the startIndex and repeat.
            startIndex += 1
        # Now increment the length of the string chunk to consider for all positions
        startSize += 1

    potentialPalindromes = []
    largestSize = 0
    for eachPalindrome in palindromeList:
        if len(eachPalindrome) > largestSize:
            largestSize = len(eachPalindrome)
            potentialPalindromes = []
            if len(eachPalindrome) == largestSize:
                potentialPalindromes.append(eachPalindrome)

    potentialPalindromes.sort()
    largestFirstPalindrome = potentialPalindromes[0]

    # Return the largest palindrome, with palindromes sorted alphabetically
    return largestFirstPalindrome

theTestString = "aoaoaoaracecarlevelnoonmadamwow"
largestPalindrome = findLargestPalindrome(theTestString)
print('The largest palindrome found in the string was: ')
print(largestPalindrome)


# O(N^2) runtime
def findLargestPalindrome(string):
    largestPalindrome = ""

    # Iterate through the characters of the input string
    for i in range(len(string)):
        # Check for odd-length palindromes
        odd_palindrome = expand_around_center(string, i, i)
        if len(odd_palindrome) > len(largestPalindrome):
            # Update largestPalindrome if a longer odd palindrome is found
            largestPalindrome = odd_palindrome

        # Check for even-length palindromes
        even_palindrome = expand_around_center(string, i, i + 1)
        if len(even_palindrome) > len(largestPalindrome):
            # Update largestPalindrome if a longer even palindrome is found
            largestPalindrome = even_palindrome

    return largestPalindrome


# Helper function to expand around the center of a potential palindrome
def expand_around_center(string, left, right):

    while left >= 0 and right < len(string) and string[left] == string[right]:
        # Expand the palindrome window while characters match
        left -= 1
        right += 1

    # Return the palindrome substring found
    return string[left + 1:right]


theTestString = "aoaoaoaracecarlevelnoonmadamwow"
largestPalindrome = findLargestPalindrome(theTestString)
print('The largest palindrome found in the string was: ')
print(largestPalindrome)
