def quickSort(arr):

    # Return the array if 1 element, or empty
    if len(arr) <= 1:
        return arr

    # Select a pivotElement, at the mid index of the array
    pivotPoint = len(arr) // 2
    pivotElement = arr[pivotPoint]

    # Separate the array into three parts, lesser and equals and greater
    left = [x for x in arr if x < pivotElement]
    middle = [x for x in arr if x == pivotElement]
    right = [x for x in arr if x > pivotElement]

    # Recurse and sort the left hand side, then sort the right hand side, then join
    left = quickSort(left)
    right = quickSort(right)

    arr = left + middle + right
    return arr


def insertionSort(arr):

    n = len(arr)

    for i in range(1, n):

        # Select item from array and index of j
        currentItem = arr[i]
        j = i - 1

        # Override item to the right of j until currentItem > arr[j]
        while j >= 0 and arr[j] > currentItem:
            arr[j + 1] = arr[j]
            j = j - 1

        # Replace currentItem in right position, now all right element are larger
        arr[j + 1] = currentItem

    return arr


def heapsort(arr):

    def heapify(arr, n, i):

        largest = i
        left = i * 2 + 1
        right = i * 2 + 2

        if left < n and arr[i] < arr[left]:
            largest = left

        if right < n and arr[largest] < arr[right]:
            largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)

    return arr


def generateSubsets(arr):

    n = len(arr)
    subsets = []

    for i in range(2 ** n):

        subset = []

        for j in range(n):
            if (i >> j) & 1:
                subset.append(arr[j])

        subsets.append(subset)

    return subsets


slashFiction = ['Jasmine', 'Abu', 'Genie', 'Jafar', 'Aladdin']
print(len(generateSubsets(slashFiction)))
print(generateSubsets(slashFiction))


testArray = [1, 5, 9, 2, 7, 3, 7, 1, 3, 1, 8, 3, 7, 2, 1]
print(quickSort(testArray))
testArray = [1, 5, 9, 2, 7, 3, 7, 1, 3, 1, 8, 3, 7, 2, 1]
print(insertionSort(testArray))
testArray = [1, 5, 9, 2, 7, 3, 7, 1, 3, 1, 8, 3, 7, 2, 1]
print(heapsort(testArray))


class Node:

    def __init__(self, value, leftChild=None, rightChild=None):
        self.value = value
        self.leftChild = leftChild
        self.rightChild = rightChild

    def updateLeft(self, leftNode):
        self.leftChild = leftNode

    def updateRight(self, rightNode):
        self.rightChild = rightNode

    def updateValue(self, newValue):
        self.value = newValue

class BinarySearchTree:

    def __init__(self, rootValue=None, leftChild=None, rightChild=None):

        self.root = Node(rootValue, leftChild, rightChild)

    def depthFirstSearch(self):
        return None

    def breadthFirstSearch(self):
        return None

testTree = BinarySearchTree(5, Node(3), Node(7))


# Order of operations not immediately apparent; can be parsed as a graph then solved. Total time is 2N.
arithmetic_operations = {
    'A': '7 + B - C',
    'B': '5 + D',
    'C': '4 - E',
    'D': '3 * F',
    'E': '2 / G',
    'F': '6 + 6 + 6',
    'G': '8 - H',
    'H': '9 + I',
    'I': '10 + 5 - 1',
}