import os
from metabeaver.Formatting.printControl import conditional_print as cprint


# Max-Heapify an array. Move largest elements to root.
def heapify(arr, n, i):

    # Print the array, length of array, and current index
    cprint('\n')
    cprint('Got array, length and index: ')
    cprint(arr)
    cprint(n)
    cprint(i)

    # Set the left and right indicies of child elements of the current node
    left = 2 * i + 1  # Calculate the index of the left child.
    right = 2 * i + 2  # Calculate the index of the right child.
    # Assume the parent node (at index i), is the largest.
    largest = i

    # Print the left and right indicies
    cprint('Left and Right indices: ')
    cprint(left)
    cprint(right)

    # If the left child exists with array bounds and is greater than the parent, update 'largest'.
    if left < n and arr[i] < arr[left]:
        largest = left

    # If the right child exists with array bounds and is greater than either parent or left child, update 'largest'.
    if right < n and arr[largest] < arr[right]:
        largest = right

    # If either the left child or the right child were larger than parent, swap them, and recurse
    if largest != i:

        # Print the array before we perform the swap
        cprint('\n')
        cprint('Array before swap was:')
        cprint(arr)

        # If the largest element is not the current node, swap them.
        cprint('Array after swap is: ')
        arr[i], arr[largest] = arr[largest], arr[i]
        cprint(arr)
        heapify(arr, n, largest)


# Build a max heap, and then sort the remainder of the heap
def heapSort(arr):


    n = len(arr)

    cprint("Building a Max Heap:")
    # Build a max heap. Shift the largest element to the root and smallest to the right.
    for i in range(n // 2 - 1, -1, -1):
        cprint(f"Heapifying at index {i}")
        heapify(arr, n, i)
        cprint(arr)

    cprint("\nSorting the remaining Heap:")
    # Sort the remainder of the array using a shrinking window. Shift remaining biggest to left, then swap.
    for i in range(n - 1, 0, -1):
        # Swap the largest element with the last element.
        cprint(f"Swapping {arr[i]} with {arr[0]}")
        arr[i], arr[0] = arr[0], arr[i]

        # Recursively shift elements to the left
        heapify(arr, i, 0)
        cprint(arr)

    return arr


# Establish a test case for heapSort and print the results if os env BEAVER_PRINTING is a string equal to "True"
os.environ["BEAVER_PRINTING"] = "True" # Update to inherit from your desired settings, e.g. test server


# Example usage:
#input_list = [13, 11, 10, 5, 6, 7]
input_list = [8, 5, 12, 1000, 1000000]
cprint("Original array:")
cprint(input_list)
sorted_list = heapSort(input_list)
cprint("\nSorted array:")
cprint(sorted_list)


# Second example with already sorted list
input_list = [1, 2, 3, 4, 5, 6]
cprint("Original array:", input_list)
sorted_list = heapSort(input_list)
cprint("\nSorted array:")
cprint(sorted_list)