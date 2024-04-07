from metabeaver.DataStructures.BinarySearchTree import BinarySearchTree

# Binary search
def binarySearch(array, target):
    """
    Perform binary search to find a target element in a sorted array.

    Args:
        array (list): The sorted input array to search in.
        target: The element to search for in the array.

    Returns:
        int: The index of the target element if found; -1 if not found.

    Pros:
    - Binary search is efficient for searching in sorted arrays.
    - It has a time complexity of O(log n), where n is the size of the array.
    - It's a fast and reliable search algorithm for large datasets.

    Cons:
    - It requires the input array to be sorted.
    - Binary search may not work efficiently when the size difference between two arrays (m and n) is significant, as it's most effective when sizes are relatively balanced.
    - It may not work well for searching unsorted data.
    - It doesn't handle duplicate values well, often returning the index of the first occurrence.

    Example:
    For balanced sizes (m and n) with k = 3:
    - Array 1 (m) has 300 elements
    - Array 2 (n) has 100 elements
    - Binary search is efficient when 100 <= m <= 300 (i.e., 100 <= 3 * 100).

    When to Use:
    - Use binary search when you have a large sorted dataset, and you need to efficiently locate a specific element within it. This is particularly valuable in scenarios where linear search would be too slow.

    """
    # Initialize left and right pointers to the array's bounds.
    left = 0
    right = len(array) - 1

    # Continue as long as the search space is not empty.
    while left <= right:
        # Calculate the midpoint of the current search space.
        middle = (left + right) // 2
        # Get the element at the midpoint.
        potentialMatch = array[middle]
        # If the target is found, return its index.
        if target == potentialMatch:
            return middle
        # If the target is less than the midpoint, adjust the right pointer.
        elif target < potentialMatch:
            right = middle - 1
        # If the target is greater than the midpoint, adjust the left pointer.
        else:
            left = middle + 1
    # If the target is not found in the array, return -1.
    return -1


# Example usage:
arrayOne = [1, 3, 5, 2, 4]
arrayTwo = [100, 100000, 10, 10000, 1000]
array = arrayOne + arrayTwo

binary_search_tree = BinarySearchTree()

for element in array:
    binary_search_tree.insert(element)

median = binary_search_tree.median()
print('The median value of the Binary Search Tree was: ')
print(median)