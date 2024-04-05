def insertionSort(arr):

    """

    5 4 3 2
    5 5 3 2
    4 5 3 2
    4 5 5 2
    4 4 5 2
    3 4 5 2
    3 4 5 5
    3 4 4 5
    3 3 4 5
    2 3 4 5

    """

    # Iterate over the whole array.
    n = len(arr)

    # Ignore the first element on its own and iterate over the rest of the arrays at index i and i-1. Starts at 0 and 1.
    for i in range(1, n):
        currentItem = arr[i]
        j = i - 1

        # While still in the array in pairs, and while the left hand bigger than the right, slide left element right.
        while j >= 0 and currentItem < arr[j]:
            # Copy the left element, to the right. We now have two copies!
            # We'll override one if we find bigger element.
            arr[j + 1] = arr[j]
            print(arr)
            j -= 1
        # When it is no longer true the elements to the left are bigger, place original element found here.
        arr[j + 1] = currentItem
        print(arr)

    # Return the sorted array
    return arr

#unsortedList = [1, 9, 3, 8, 2, 9, 1, 4, 8, 2, 13]
#unsortedList = [8, 2, 3, 4, 9, 7]
unsortedList = [5, 5, 4, 3, 1]
print(insertionSort(unsortedList))


"""

def insertionSort(arr):
    n = len(arr)
    for i in range(1, n):
        currentItem = arr[i]
        j = i - 1
        while j >= 0 and currentItem < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = currentItem
    return arr

unsortedList = [5, 4, 3]
print(insertionSort(unsortedList))

"""