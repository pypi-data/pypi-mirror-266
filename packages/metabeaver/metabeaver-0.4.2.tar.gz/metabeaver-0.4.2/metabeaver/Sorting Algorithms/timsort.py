def insertion_sort(arr, left=0, right=None):
    """
    Perform an insertion sort on a given portion of the array.

    This function performs an insertion sort on the given portion of the array.
    It works by repeatedly comparing the current element with the elements to its left, and shifting them to the right.
    The right shift continues until the correct position is found.

    :param arr: The input array to be sorted.
    :param left: The left index of the portion to be sorted.
    :param right: The right index of the portion to be sorted.
    :return: The sorted array.
    """

    if right is None:
        right = len(arr) - 1

    # Iterate through the portion of the array to be sorted.
    for i in range(left + 1, right + 1):
        # Pick the next element to be inserted.
        key_item = arr[i]
        j = i - 1

        # Compare and shift elements to the right until the correct position is found.
        while j >= left and arr[j] > key_item:
            arr[j + 1] = arr[j]
            j -= 1

        # Place the selected element at its correct position.
        arr[j + 1] = key_item

    return arr





def merge(left, right):
    """
    Merge two sorted arrays into a single sorted array.

    # This function merges two sorted arrays into a single sorted array.
    # It repeatedly compares the first elements of the two arrays and adds the smaller element to the merged array.
    # Then, the corresponding array is shortened by one element.
    # This process continues until one of the arrays is empty.

    :param left: The left array.
    :param right: The right array.
    :return: The merged and sorted array.
    """

    if not left:
        return right

    if not right:
        return left

    if left[0] < right[0]:
        return [left[0]] + merge(left[1:], right)
    else:
        return [right[0]] + merge(left, right[1:])






def timsort(arr):
    """
    Sort an array using the Timsort algorithm.

    This function sorts an array using the Timsort algorithm.
    It works by first dividing the array into small chunks called runs.
    Each run is then sorted using insertion sort.
    Next, the runs are merged together in pairs until the entire array is sorted.

    :param arr: The input array to be sorted.
    :return: The sorted array.
    """

    # Set the minimum run size for insertion sort.
    min_run = 32
    n = len(arr)

    for i in range(0, n, min_run):
        # Apply insertion sort on small chunks of the array.
        insertion_sort(arr, i, min((i + min_run - 1), n - 1))

    size = min_run

    while size < n:
        for start in range(0, n, size * 2):
            # Merge sorted chunks of the array.
            midpoint = min((start + size - 1), (n - 1))
            end = min((start + size * 2 - 1), (n - 1))

            merged_array = merge(left=arr[start:midpoint + 1], right=arr[midpoint + 1:end + 1])
            arr[start:start + len(merged_array)] = merged_array

        size *= 2

    return arr




unsorted_list = [4, 1, 3, 9, 6, 2, 8, 7, 5]
sorted_list = timsort(unsorted_list)
print(sorted_list)
