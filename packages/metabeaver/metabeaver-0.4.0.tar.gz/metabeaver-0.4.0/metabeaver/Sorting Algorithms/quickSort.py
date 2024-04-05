# Take an array and recursively sorts around a pivot that defines right and lefthand sides
def quickSort(arr):

    """
    Runtime average case of n log n and runtime worst case of n squared
    Space complexity of log n

    :param arr:

    returns a sorted array.

    """

    # Return the array if we've segmented into 1 or less elements
    if len(arr) <= 1:
        return arr

    # Define a pivot point and select the element to pivot over
    pivotPoint = len(arr) // 2
    pivotElement = arr[pivotPoint]

    # Sort the array into left, middle, and right sections based on the value of the pivot
    left = [x for x in arr if x < pivotElement]
    middle = [x for x in arr if x == pivotElement]
    right = [x for x in arr if x > pivotElement]

    # Recurse, travelling left first, which will return sorted stack of left elements, then add right and middle
    left = quickSort(left)
    right = quickSort(right)
    sortedArray = left + middle + right

    # Return the sortedArray
    return sortedArray

testArray = [3, 8, 1, 2, 5, 1, 17, 3, 9, 2, 6, 3]
print(quickSort(testArray))

